import { Sale, Product } from "../types/models";

export function validateSale(sale: Sale): boolean {
  return (
    sale.amount > 0 &&
    sale.restaurantId.length > 0 &&
    sale.date instanceof Date
  );
}

export function validateProduct(product: Product): boolean {
  return product.price > 0 && product.name.length > 0;
}