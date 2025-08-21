import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export async function POST(
  request: NextRequest,
  { params }: { params: { tripId: string } }
) {
  try {
    const { tripId } = params;
    
    // Trigger guide generation on backend
    const response = await fetch(`${BACKEND_URL}/api/generate-guide/${tripId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend generation error:', errorText);
      return NextResponse.json(
        { error: 'Failed to generate guide' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Generation proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to generate guide' },
      { status: 500 }
    );
  }
}