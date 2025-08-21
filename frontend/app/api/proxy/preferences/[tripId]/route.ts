import { NextRequest, NextResponse } from 'next/server';

export async function POST(
  request: NextRequest,
  { params }: { params: { tripId: string } }
) {
  const tripId = params.tripId;
  const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

  try {
    const body = await request.json();
    
    const response = await fetch(`${BACKEND_URL}/api/preferences/${tripId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Preferences API error:', errorText);
      return NextResponse.json(
        { status: 'error', message: 'Failed to update preferences' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Preferences proxy error:', error);
    return NextResponse.json(
      { status: 'error', message: 'Connection error' },
      { status: 500 }
    );
  }
}