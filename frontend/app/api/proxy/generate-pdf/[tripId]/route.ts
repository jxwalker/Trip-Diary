import { NextRequest, NextResponse } from 'next/server';

export async function POST(
  request: NextRequest,
  { params }: { params: { tripId: string } }
) {
  const tripId = params.tripId;
  const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

  try {
    const response = await fetch(`${BACKEND_URL}/api/generate-pdf/${tripId}`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      return NextResponse.json(
        { status: 'error', message: 'Failed to generate PDF' },
        { status: response.status }
      );
    }

    // Stream the PDF back to the client
    const headers = new Headers(response.headers);
    headers.set('Content-Type', 'application/pdf');
    // Preserve filename if backend set it
    const cd = response.headers.get('Content-Disposition') || `attachment; filename="travel_pack_${tripId}.pdf"`;
    headers.set('Content-Disposition', cd);
    return new NextResponse(response.body, { status: 200, headers });
  } catch (error) {
    console.error('Generate PDF proxy error:', error);
    return NextResponse.json(
      { status: 'error', message: 'Connection error' },
      { status: 500 }
    );
  }
}