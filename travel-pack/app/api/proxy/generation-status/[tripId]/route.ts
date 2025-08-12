import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: { tripId: string } }
) {
  const tripId = params.tripId;

  try {
    const response = await fetch(`http://localhost:8000/api/generation-status/${tripId}`);
    
    if (!response.ok) {
      return NextResponse.json(
        { status: 'error', message: 'Failed to get status' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Status proxy error:', error);
    return NextResponse.json(
      { status: 'error', message: 'Connection error' },
      { status: 500 }
    );
  }
}