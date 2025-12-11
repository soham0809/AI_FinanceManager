"""
AI Financial Co-Pilot API - Modular Backend
Main FastAPI application with authentication and modular architecture
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.config.database import engine, Base
from app.routes import auth_routes, transaction_routes, analytics_routes, batch_routes, chatbot_routes, quick_routes, intelligent_filter_routes, enhanced_transaction_routes, spending_analytics_routes, intelligent_query_routes, enhanced_chatbot_routes, predictions_routes, categorize_routes
from app.models import user, transaction

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_routes.router)
app.include_router(transaction_routes.router)
app.include_router(analytics_routes.router)
app.include_router(batch_routes.router)
app.include_router(chatbot_routes.router)
app.include_router(quick_routes.router)
app.include_router(intelligent_filter_routes.router)
app.include_router(enhanced_transaction_routes.router)
app.include_router(spending_analytics_routes.router)
app.include_router(intelligent_query_routes.router)
app.include_router(enhanced_chatbot_routes.router)
app.include_router(predictions_routes.router)
app.include_router(categorize_routes.router)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "message": "All systems operational",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
