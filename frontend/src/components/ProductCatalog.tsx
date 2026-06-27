import React from 'react';
import { ShoppingBag } from 'lucide-react';
import type { Product } from '../services/api';

interface ProductCatalogProps {
  recommendedProducts: Record<string, Product[]>;
}

export const ProductCatalog: React.FC<ProductCatalogProps> = ({ recommendedProducts }) => {
  return (
    <div className="shop-categories-list fade-in">
      <div className="shop-header">
        <h4 className="shop-title">Recommended Shop Catalog</h4>
        <p className="shop-subtitle">Cosmetics from our catalog matching your skin undertone.</p>
      </div>
      
      {Object.keys(recommendedProducts).length === 0 ? (
        <div className="text-center py-12 text-sm text-gray-500">
          No recommendations found. Upload a photo to scan products.
        </div>
      ) : (
        <div className="shop-categories-list max-h-[350px] overflow-y-auto pr-1">
          {Object.entries(recommendedProducts).map(([category, items]) => (
            <div key={category} className="shop-category-section mb-4">
              <h5 className="shop-category-title">{category}</h5>
              <div>
                {items.map((prod) => (
                  <div 
                    key={prod.id} 
                    className="product-item"
                  >
                    <div className="product-item-details">
                      <span 
                        className="product-swatch"
                        style={{ backgroundColor: prod.hex_color }}
                      />
                      <div className="product-meta">
                        <span className="product-name">{prod.name}</span>
                        <span className="product-brand-finish">{prod.brand} • {prod.finish}</span>
                      </div>
                    </div>
                    <div className="product-actions">
                      <span className="product-price">${prod.price.toFixed(2)}</span>
                      <button 
                        onClick={() => alert(`Redirecting to shop item: ${prod.brand} ${prod.name}`)}
                        className="product-buy-btn flex items-center justify-center border-0 cursor-pointer"
                      >
                        <ShoppingBag className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
