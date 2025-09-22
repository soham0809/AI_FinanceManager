"""
Phase 6: Group Expenses Management
Handles expense splitting and group financial management
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from database import Base
from datetime import datetime
from typing import List, Dict, Optional
import json

class Group(Base):
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_by = Column(String, nullable=False)  # User identifier
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    members = relationship("GroupMember", back_populates="group")
    expenses = relationship("GroupExpense", back_populates="group")

class GroupMember(Base):
    __tablename__ = "group_members"
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    user_identifier = Column(String, nullable=False)  # Phone number or email
    name = Column(String, nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    group = relationship("Group", back_populates="members")

class GroupExpense(Base):
    __tablename__ = "group_expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    paid_by = Column(String, nullable=False)  # User identifier who paid
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=False)
    category = Column(String, default="Other")
    date = Column(DateTime, default=datetime.utcnow)
    split_method = Column(String, default="equal")  # equal, percentage, custom
    split_data = Column(Text)  # JSON data for split details
    
    # Relationships
    group = relationship("Group", back_populates="expenses")
    settlements = relationship("ExpenseSettlement", back_populates="expense")

class ExpenseSettlement(Base):
    __tablename__ = "expense_settlements"
    
    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, ForeignKey("group_expenses.id"))
    user_identifier = Column(String, nullable=False)
    amount_owed = Column(Float, nullable=False)
    amount_paid = Column(Float, default=0.0)
    is_settled = Column(Boolean, default=False)
    settled_at = Column(DateTime)
    
    # Relationships
    expense = relationship("GroupExpense", back_populates="settlements")

class GroupExpenseManager:
    """Manager class for group expense operations"""
    
    def create_group(self, db: Session, name: str, description: str, created_by: str) -> Group:
        """Create a new expense group"""
        group = Group(
            name=name,
            description=description,
            created_by=created_by
        )
        db.add(group)
        db.commit()
        db.refresh(group)
        
        # Add creator as first member
        self.add_member(db, group.id, created_by, "Creator")
        
        return group
    
    def add_member(self, db: Session, group_id: int, user_identifier: str, name: str) -> GroupMember:
        """Add a member to a group"""
        member = GroupMember(
            group_id=group_id,
            user_identifier=user_identifier,
            name=name
        )
        db.add(member)
        db.commit()
        db.refresh(member)
        return member
    
    def add_expense(self, db: Session, group_id: int, paid_by: str, amount: float, 
                   description: str, category: str = "Other", 
                   split_method: str = "equal", split_data: Dict = None) -> GroupExpense:
        """Add an expense to a group"""
        
        # Get group members for equal split calculation
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            raise ValueError("Group not found")
        
        active_members = db.query(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.is_active == True
        ).all()
        
        if not active_members:
            raise ValueError("No active members in group")
        
        # Create expense
        expense = GroupExpense(
            group_id=group_id,
            paid_by=paid_by,
            amount=amount,
            description=description,
            category=category,
            split_method=split_method,
            split_data=json.dumps(split_data) if split_data else None
        )
        db.add(expense)
        db.commit()
        db.refresh(expense)
        
        # Calculate and create settlements
        self._create_settlements(db, expense, active_members, split_method, split_data)
        
        return expense
    
    def _create_settlements(self, db: Session, expense: GroupExpense, 
                          members: List[GroupMember], split_method: str, split_data: Dict):
        """Create settlement records for an expense"""
        
        if split_method == "equal":
            amount_per_person = expense.amount / len(members)
            
            for member in members:
                if member.user_identifier != expense.paid_by:
                    settlement = ExpenseSettlement(
                        expense_id=expense.id,
                        user_identifier=member.user_identifier,
                        amount_owed=amount_per_person
                    )
                    db.add(settlement)
        
        elif split_method == "percentage" and split_data:
            for member in members:
                if member.user_identifier != expense.paid_by:
                    percentage = split_data.get(member.user_identifier, 0)
                    amount_owed = expense.amount * (percentage / 100)
                    
                    settlement = ExpenseSettlement(
                        expense_id=expense.id,
                        user_identifier=member.user_identifier,
                        amount_owed=amount_owed
                    )
                    db.add(settlement)
        
        elif split_method == "custom" and split_data:
            for member in members:
                if member.user_identifier != expense.paid_by:
                    amount_owed = split_data.get(member.user_identifier, 0)
                    
                    settlement = ExpenseSettlement(
                        expense_id=expense.id,
                        user_identifier=member.user_identifier,
                        amount_owed=amount_owed
                    )
                    db.add(settlement)
        
        db.commit()
    
    def get_group_summary(self, db: Session, group_id: int) -> Dict:
        """Get comprehensive group expense summary"""
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            raise ValueError("Group not found")
        
        members = db.query(GroupMember).filter(
            GroupMember.group_id == group_id,
            GroupMember.is_active == True
        ).all()
        
        expenses = db.query(GroupExpense).filter(
            GroupExpense.group_id == group_id
        ).all()
        
        # Calculate balances
        balances = {}
        for member in members:
            balances[member.user_identifier] = {
                'name': member.name,
                'total_paid': 0.0,
                'total_owed': 0.0,
                'net_balance': 0.0
            }
        
        # Calculate what each member paid
        for expense in expenses:
            if expense.paid_by in balances:
                balances[expense.paid_by]['total_paid'] += expense.amount
        
        # Calculate what each member owes
        for expense in expenses:
            settlements = db.query(ExpenseSettlement).filter(
                ExpenseSettlement.expense_id == expense.id
            ).all()
            
            for settlement in settlements:
                if settlement.user_identifier in balances:
                    balances[settlement.user_identifier]['total_owed'] += settlement.amount_owed
        
        # Calculate net balances
        for user_id, balance in balances.items():
            balance['net_balance'] = balance['total_paid'] - balance['total_owed']
        
        return {
            'group': {
                'id': group.id,
                'name': group.name,
                'description': group.description,
                'created_by': group.created_by,
                'created_at': group.created_at.isoformat()
            },
            'members': [
                {
                    'user_identifier': member.user_identifier,
                    'name': member.name,
                    'joined_at': member.joined_at.isoformat()
                } for member in members
            ],
            'total_expenses': sum(expense.amount for expense in expenses),
            'expense_count': len(expenses),
            'balances': balances,
            'recent_expenses': [
                {
                    'id': expense.id,
                    'description': expense.description,
                    'amount': expense.amount,
                    'paid_by': expense.paid_by,
                    'category': expense.category,
                    'date': expense.date.isoformat()
                } for expense in sorted(expenses, key=lambda x: x.date, reverse=True)[:10]
            ]
        }
    
    def settle_expense(self, db: Session, settlement_id: int, amount_paid: float) -> ExpenseSettlement:
        """Record a settlement payment"""
        settlement = db.query(ExpenseSettlement).filter(
            ExpenseSettlement.id == settlement_id
        ).first()
        
        if not settlement:
            raise ValueError("Settlement not found")
        
        settlement.amount_paid += amount_paid
        
        if settlement.amount_paid >= settlement.amount_owed:
            settlement.is_settled = True
            settlement.settled_at = datetime.utcnow()
        
        db.commit()
        db.refresh(settlement)
        return settlement
    
    def get_user_groups(self, db: Session, user_identifier: str) -> List[Dict]:
        """Get all groups for a user"""
        memberships = db.query(GroupMember).filter(
            GroupMember.user_identifier == user_identifier,
            GroupMember.is_active == True
        ).all()
        
        groups = []
        for membership in memberships:
            group_summary = self.get_group_summary(db, membership.group_id)
            groups.append(group_summary)
        
        return groups
    
    def get_pending_settlements(self, db: Session, user_identifier: str) -> List[Dict]:
        """Get all pending settlements for a user"""
        settlements = db.query(ExpenseSettlement).filter(
            ExpenseSettlement.user_identifier == user_identifier,
            ExpenseSettlement.is_settled == False
        ).all()
        
        pending = []
        for settlement in settlements:
            expense = db.query(GroupExpense).filter(
                GroupExpense.id == settlement.expense_id
            ).first()
            
            group = db.query(Group).filter(
                Group.id == expense.group_id
            ).first()
            
            pending.append({
                'settlement_id': settlement.id,
                'expense_description': expense.description,
                'amount_owed': settlement.amount_owed,
                'amount_paid': settlement.amount_paid,
                'remaining': settlement.amount_owed - settlement.amount_paid,
                'group_name': group.name,
                'paid_by': expense.paid_by,
                'date': expense.date.isoformat()
            })
        
        return pending

# Global instance
group_expense_manager = GroupExpenseManager()
