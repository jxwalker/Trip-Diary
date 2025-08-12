"""
Test API endpoints
"""
import pytest
import json
from httpx import AsyncClient
import asyncio

class TestAPIEndpoints:
    """Test main API endpoints."""
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self, async_client: AsyncClient):
        """Test root endpoint returns API info."""
        response = await async_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["message"] == "TripCraft AI API is running"
    
    @pytest.mark.asyncio
    async def test_upload_with_manual_data(self, async_client: AsyncClient, sample_trip_data):
        """Test upload endpoint with manual trip data."""
        response = await async_client.post(
            "/api/upload",
            data={
                "trip_details": json.dumps(sample_trip_data),
                "free_text": "Flight AA123 from JFK to CDG"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "trip_id" in data
        assert data["status"] == "processing"
        assert data["progress"] == 10
    
    @pytest.mark.asyncio
    async def test_upload_with_files(self, async_client: AsyncClient, sample_pdf_path):
        """Test upload endpoint with PDF file."""
        with open(sample_pdf_path, "rb") as f:
            files = {"files": ("test.pdf", f, "application/pdf")}
            response = await async_client.post(
                "/api/upload",
                files=files
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "trip_id" in data
        assert data["status"] == "processing"
    
    @pytest.mark.asyncio
    async def test_status_endpoint(self, async_client: AsyncClient, sample_trip_data):
        """Test status checking endpoint."""
        # First create a trip
        upload_response = await async_client.post(
            "/api/upload",
            data={
                "trip_details": json.dumps(sample_trip_data)
            }
        )
        trip_id = upload_response.json()["trip_id"]
        
        # Wait a bit for processing
        await asyncio.sleep(2)
        
        # Check status
        status_response = await async_client.get(f"/api/status/{trip_id}")
        assert status_response.status_code == 200
        data = status_response.json()
        assert data["trip_id"] == trip_id
        assert "status" in data
        assert "progress" in data
    
    @pytest.mark.asyncio
    async def test_status_invalid_trip_id(self, async_client: AsyncClient):
        """Test status endpoint with invalid trip ID."""
        response = await async_client.get("/api/status/invalid-id-123")
        assert response.status_code == 404
        assert "Trip ID not found" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_itinerary_endpoint(self, async_client: AsyncClient, sample_trip_data):
        """Test itinerary retrieval endpoint."""
        # Create and process a trip
        upload_response = await async_client.post(
            "/api/upload",
            data={
                "trip_details": json.dumps(sample_trip_data)
            }
        )
        trip_id = upload_response.json()["trip_id"]
        
        # Wait for processing to complete
        max_attempts = 10
        for _ in range(max_attempts):
            status_response = await async_client.get(f"/api/status/{trip_id}")
            if status_response.json()["status"] == "completed":
                break
            await asyncio.sleep(1)
        
        # Get itinerary
        itinerary_response = await async_client.get(f"/api/itinerary/{trip_id}")
        assert itinerary_response.status_code == 200
        data = itinerary_response.json()
        assert "trip_id" in data
        assert "itinerary" in data
        assert "recommendations" in data
    
    @pytest.mark.asyncio
    async def test_pdf_generation(self, async_client: AsyncClient, sample_trip_data):
        """Test PDF generation endpoint."""
        # Create and process a trip
        upload_response = await async_client.post(
            "/api/upload",
            data={
                "trip_details": json.dumps(sample_trip_data)
            }
        )
        trip_id = upload_response.json()["trip_id"]
        
        # Wait for processing
        max_attempts = 10
        for _ in range(max_attempts):
            status_response = await async_client.get(f"/api/status/{trip_id}")
            if status_response.json()["status"] == "completed":
                break
            await asyncio.sleep(1)
        
        # Generate PDF
        pdf_response = await async_client.post(f"/api/generate-pdf/{trip_id}")
        assert pdf_response.status_code == 200
        data = pdf_response.json()
        assert data["status"] == "success"
        assert "pdf_url" in data
    
    @pytest.mark.asyncio
    async def test_preferences_update(self, async_client: AsyncClient, sample_trip_data):
        """Test preferences update endpoint."""
        # Create a trip
        upload_response = await async_client.post(
            "/api/upload",
            data={
                "trip_details": json.dumps(sample_trip_data)
            }
        )
        trip_id = upload_response.json()["trip_id"]
        
        # Wait for processing
        await asyncio.sleep(3)
        
        # Update preferences
        preferences = {
            "budget": "high",
            "cuisine_preferences": ["French", "Italian"],
            "interests": ["art", "history"]
        }
        
        pref_response = await async_client.post(
            f"/api/preferences/{trip_id}",
            json=preferences
        )
        assert pref_response.status_code == 200
        data = pref_response.json()
        assert data["status"] == "success"