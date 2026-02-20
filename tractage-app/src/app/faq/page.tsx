import { FAQ_DATA, CATEGORIES } from '@/lib/faqData';
import { FAQByCategory } from '@/components/FAQ';

export const metadata = {
  title: 'Foire Aux Questions - Notre programme',
  description: 'Trouvez les réponses à vos questions sur notre programme politique pour Les Sables d\'Olonne',
};

export default function FAQPage() {
  return (
    <main className="min-h-screen bg-gray-50">
      {/* En-tête */}
      <div className="bg-white border-b border-gray-200 py-12">
        <div className="max-w-4xl mx-auto px-6">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Foire Aux Questions
          </h1>
          <p className="text-xl text-gray-600">
            Découvrez les réponses à vos questions sur notre programme pour Les Sables d'Olonne.
            Nous avons compilé les questions les plus fréquemment posées par les citoyens.
          </p>
        </div>
      </div>

      {/* Contenu Principal */}
      <div className="max-w-4xl mx-auto px-6 py-12">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <FAQByCategory items={FAQ_DATA} categories={CATEGORIES} />
        </div>

        {/* Autres questions? */}
        <div className="mt-12 bg-blue-50 border border-blue-200 rounded-lg p-8 text-center">
          <h2 className="text-2xl font-bold text-blue-900 mb-4">
            Vous avez une autre question ?
          </h2>
          <p className="text-blue-700 mb-6">
            Notre équipe est disponible pour répondre à vos questions spécifiques. Contactez-nous !
          </p>
          <button className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-3 px-8 rounded-lg transition-colors">
            Nous contacter
          </button>
        </div>
      </div>
    </main>
  );
}
