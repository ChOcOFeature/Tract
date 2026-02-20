import { NextRequest, NextResponse } from 'next/server';
import { FAQ_DATA, CATEGORIES } from '@/lib/faqData';
import { FAQItem } from '@/types/index';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const categorie = searchParams.get('categorie');
    const segment = searchParams.get('segment');
    const search = searchParams.get('search');

    let results: FAQItem[] = FAQ_DATA;

    // Filtrer par catégorie
    if (categorie && CATEGORIES.includes(categorie)) {
      results = results.filter(item => item.categorie === categorie);
    }

    // Filtrer par segment (éléphant)
    if (segment) {
      results = results.filter(item => {
        // Si pas de segments spécifiés, c'est une FAQ générale
        if (!item.segments || item.segments.length === 0) return true;
        return item.segments.includes(segment);
      });
    }

    // Recherche textuelle
    if (search) {
      const searchLower = search.toLowerCase();
      results = results.filter(item =>
        item.question.toLowerCase().includes(searchLower) ||
        item.reponse.toLowerCase().includes(searchLower) ||
        item.categorie.toLowerCase().includes(searchLower)
      );
    }

    return NextResponse.json({
      success: true,
      data: results,
      categories: CATEGORIES,
      total: results.length,
    });
  } catch (error) {
    console.error('Erreur lors de la récupération de la FAQ:', error);
    return NextResponse.json(
      {
        success: false,
        message: 'Erreur lors de la récupération de la FAQ',
      },
      { status: 500 }
    );
  }
}
