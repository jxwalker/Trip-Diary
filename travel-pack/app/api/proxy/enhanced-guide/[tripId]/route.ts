import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: { tripId: string } }
) {
  const tripId = params.tripId;
  const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

  try {
    const response = await fetch(`${BACKEND_URL}/api/enhanced-guide/${tripId}`);
    
    if (!response.ok) {
      return NextResponse.json(
        { status: 'error', message: 'Guide not found' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Enhanced guide proxy error:', error);
    return NextResponse.json(
      { status: 'error', message: 'Connection error' },
      { status: 500 }
    );
  }
}