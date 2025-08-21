import { NextRequest } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: { tripId: string } }
) {
  const tripId = params.tripId;
  const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

  // Create a readable stream for SSE
  const stream = new ReadableStream({
    async start(controller) {
      const encoder = new TextEncoder();
      
      try {
        // Connect to backend SSE endpoint
        const response = await fetch(`${BACKEND_URL}/api/generation-stream/${tripId}`, {
          headers: {
            'Accept': 'text/event-stream',
          },
        });

        if (!response.ok || !response.body) {
          controller.enqueue(encoder.encode(`data: ${JSON.stringify({ 
            status: 'error', 
            message: 'Failed to connect to backend' 
          })}\n\n`));
          controller.close();
          return;
        }

        const reader = response.body.getReader();
        
        while (true) {
          const { done, value } = await reader.read();
          
          if (done) {
            controller.close();
            break;
          }
          
          // Forward the SSE data
          controller.enqueue(value);
        }
      } catch (error) {
        console.error('SSE proxy error:', error);
        controller.enqueue(encoder.encode(`data: ${JSON.stringify({ 
          status: 'error', 
          message: 'Connection error' 
        })}\n\n`));
        controller.close();
      }
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  });
}