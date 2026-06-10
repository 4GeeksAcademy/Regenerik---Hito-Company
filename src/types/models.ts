export type Currency = "COP" | "USD";

export interface Restaurant {
  id: string;
  name: string;
  city: string;
  country: string;
}

export interface Product {
  id: string;
  name: string;
  category: string;
  price: number;
}

export interface Sale {
  id: string;
  restaurantId: string;
  amount: number;
  currency: Currency;
  date: Date;
}

export interface Order {
  id: string;
  products: Product[];
  total: number;
  date: Date;
}

export interface Customer {
  id: string;
  name: string;
  email: string;
}