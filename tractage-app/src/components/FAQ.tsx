'use client';

import { useState } from 'react';
import { ChevronDown } from 'lucide-react';
import { FAQItem } from '@/types/index';
import clsx from 'clsx';

interface FAQProps {
  items: FAQItem[];
  animateTítles?: boolean;
  expandAll?: boolean;
}

export function FAQ({ items, animateTítles = false, expandAll = false }: FAQProps) {
  const [expandedId, setExpandedId] = useState<string | null>(expandAll ? items[0]?.id : null);

  const toggleExpanded = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <div className="w-full space-y-4">
      {items.map((item) => (
        <div
          key={item.id}
          className="border border-gray-200 rounded-lg overflow-hidden hover:border-gray-300 transition-colors"
        >
          <button
            onClick={() => toggleExpanded(item.id)}
            className="w-full px-6 py-4 flex items-center justify-between bg-white hover:bg-gray-50 transition-colors"
          >
            <div className="flex-1 text-left">
              <h3 className={clsx(
                'font-semibold text-gray-900 text-lg',
                animateTítles && 'transition-colors'
              )}>
                {item.question}
              </h3>
              <p className="text-sm text-gray-500 mt-1">
                {item.categorie}
              </p>
            </div>
            <ChevronDown
              className={clsx(
                'w-5 h-5 text-gray-400 transition-transform duration-200 flex-shrink-0 ml-4',
                expandedId === item.id && 'transform rotate-180'
              )}
            />
          </button>

          {expandedId === item.id && (
            <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
              <p className="text-gray-700 leading-relaxed">
                {item.reponse}
              </p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

interface FAQByCategoryProps {
  items: FAQItem[];
  categories: string[];
}

export function FAQByCategory({ items, categories }: FAQByCategoryProps) {
  const [activeCategory, setActiveCategory] = useState<string>(categories[0]);

  const filteredItems = items.filter(item => item.categorie === activeCategory);

  return (
    <div className="w-full">
      {/* Catégories */}
      <div className="flex flex-wrap gap-2 mb-8">
        {categories.map((category) => {
          const count = items.filter(item => item.categorie === category).length;
          return (
            <button
              key={category}
              onClick={() => setActiveCategory(category)}
              className={clsx(
                'px-4 py-2 rounded-lg font-medium transition-colors text-sm',
                activeCategory === category
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              )}
            >
              {category}
              <span className="ml-2 text-xs opacity-75">
                ({count})
              </span>
            </button>
          );
        })}
      </div>

      {/* FAQ Items */}
      <FAQ items={filteredItems} />
    </div>
  );
}
