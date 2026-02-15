import { NextResponse } from 'next/server';
import { decryptBuffer } from '@/lib/crypto';

export const runtime = 'nodejs';

export async function GET() {
  const blobUrl = process.env.ELECTEURS_BLOB_URL;
  const token = process.env.BLOB_READ_WRITE_TOKEN;
  const passphrase = process.env.ELECTEURS_PASSPHRASE;

  if (!blobUrl || !token || !passphrase) {
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

  const encryptedBuffer = Buffer.from(await response.arrayBuffer());

  let csvText = '';
  try {
    csvText = decryptBuffer(encryptedBuffer, passphrase).toString('utf8');
  } catch (error) {
    return NextResponse.json(
      { error: 'Impossible de dechiffrer le CSV.' },
      { status: 500 }
    );
  }

  return new NextResponse(csvText, {
    headers: {
      'Content-Type': 'text/csv; charset=utf-8',
      'Cache-Control': 'no-store',
    },
  });
}
