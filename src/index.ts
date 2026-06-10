import { Product, Sale } from "./types/models";
import { filterBy, sortBy, groupBy } from "./utils/collections";
import { linearSearch } from "./utils/search";
import { sum, average } from "./utils/transformations";
import { validateSale } from "./utils/validations";

// Data de prueba
const products: Product[] = [
  { id: "1", name: "Burger", category: "food", price: 10 },
  { id: "2", name: "Pizza", category: "food", price: 15 },
  { id: "3", name: "Soda", category: "drink", price: 5 }
];

const sales: Sale[] = [
  { id: "1", restaurantId: "r1", amount: 100, currency: "USD", date: new Date() },
  { id: "2", restaurantId: "r1", amount: 200, currency: "USD", date: new Date() }
];

// FILTER
const cheapProducts = filterBy(products, p => p.price < 12);

// SORT
const sortedProducts = sortBy(products, (a, b) => a.price - b.price);

// GROUP
const grouped = groupBy(products, p => p.category);

// SEARCH
const found = linearSearch(products, p => p.name === "Pizza");

// TRANSFORM
const totalSales = sum(sales.map(s => s.amount));
const avgSales = average(sales.map(s => s.amount));

// VALIDATION
const firstSale = sales[0];
const valid = firstSale ? validateSale(firstSale) : false;

console.log({ cheapProducts, sortedProducts, grouped, found, totalSales, avgSales, valid });

console.log("Proyecto funcionando 🚀");