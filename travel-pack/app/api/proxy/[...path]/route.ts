import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = 'http://localhost:8000';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path: pathArray } = await params;
  const path = pathArray.join('/');
  const url = `${BACKEND_URL}/api/${path}${request.nextUrl.search}`;
  
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Proxy error:', error);
    return NextResponse.json(
      { error: 'Backend connection failed' },
      { status: 500 }
    );
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path: pathArray } = await params;
  const path = pathArray.join('/');
  const url = `${BACKEND_URL}/api/${path}`;
  
  try {
    // Get the body - handle both FormData and JSON
    const contentType = request.headers.get('content-type');
    let response;
    
    if (contentType?.includes('multipart/form-data')) {
      // For file uploads, get the FormData and forward it
      const formData = await request.formData();
      
      // Create a new FormData to send to backend
      const backendFormData = new FormData();
      
      // Copy all fields from the incoming FormData
      for (const [key, value] of formData.entries()) {
        backendFormData.append(key, value);
      }
      
      // Send to backend without setting Content-Type (let fetch set it with boundary)
      response = await fetch(url, {
        method: 'POST',
        body: backendFormData,
      });
    } else {
      // For JSON requests
      const body = await request.text();
      response = await fetch(url, {
        method: 'POST',
        body: body,
        headers: {
          'Content-Type': contentType || 'application/json',
        },
      });
    }
    
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Proxy error:', error);
    console.error('Failed URL:', url);
    return NextResponse.json(
      { error: 'Backend connection failed', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path: pathArray } = await params;
  const path = pathArray.join('/');
  const url = `${BACKEND_URL}/api/${path}`;
  
  try {
    const body = await request.json();
    const response = await fetch(url, {
      method: 'PUT',
      body: JSON.stringify(body),
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('Proxy error:', error);
    return NextResponse.json(
      { error: 'Backend connection failed' },
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path: pathArray } = await params;
  const path = pathArray.join('/');
  const url = `${BACKEND_URL}/api/${path}`;
  
  try {
    const response = await fetch(url, {
      method: 'DELETE',
    });
    
    if (response.ok) {
      return NextResponse.json({ success: true }, { status: 200 });
    } else {
      const data = await response.json();
      return NextResponse.json(data, { status: response.status });
    }
  } catch (error) {
    console.error('Proxy error:', error);
    return NextResponse.json(
      { error: 'Backend connection failed' },
      { status: 500 }
    );
  }
}