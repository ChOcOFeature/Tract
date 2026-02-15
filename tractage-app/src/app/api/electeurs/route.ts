import { NextResponse } from 'next/server';

export const runtime = 'nodejs';

export async function GET() {
  const blobUrl = process.env.ELECTEURS_BLOB_URL;
  const token = process.env.BLOB_READ_WRITE_TOKEN;

  if (!blobUrl || !token) {
    return NextResponse.json(
      { error: 'Configuration manquante pour le CSV.' },
      { status: 500 }
    );
  }

  const response = await fetch(blobUrl, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
    cache: 'no-store',
  });

  if (!response.ok) {
    return NextResponse.json(
      { error: 'Impossible de charger le CSV.' },
      { status: 502 }
    );
  }

  const csvText = await response.text();

  return new NextResponse(csvText, {
    headers: {
      'Content-Type': 'text/csv; charset=utf-8',
      'Cache-Control': 'no-store',
    },
  });
}
