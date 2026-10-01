"use client";

import { useEffect, useState } from "react";

import { api } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

type ProductData = {
  produto_id: string;
  categoria: string;
  descricao: string;
  status: string;
  timestamp: string;
  peso: number;
  altura: number;
};

export function DataTable() {
  const [data, setData] = useState<ProductData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.get<ProductData[]>("/api/ultimos_produtos");
        setData(response.data);
        setError("");
      } catch {
        setError("Erro ao carregar dados.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const intervalId = window.setInterval(fetchData, 5000);
    return () => window.clearInterval(intervalId);
  }, []);

  if (loading) {
    return <div>Carregando...</div>;
  }

  if (error) {
    return <div>{error}</div>;
  }

  return (
    <div className="rounded-lg bg-white p-4 shadow">
      <h3 className="mb-4 text-lg font-semibold">Últimos produtos processados</h3>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>ID do produto</TableHead>
            <TableHead>Categoria</TableHead>
            <TableHead>Descrição</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Data e hora</TableHead>
            <TableHead>Peso</TableHead>
            <TableHead>Altura</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.map((item, index) => (
            <TableRow key={`${item.produto_id}-${item.timestamp}-${index}`}>
              <TableCell>{item.produto_id}</TableCell>
              <TableCell>{item.categoria}</TableCell>
              <TableCell>{item.descricao}</TableCell>
              <TableCell>
                <Badge variant={item.status === "Válido" ? "secondary" : "destructive"}>
                  {item.status}
                </Badge>
              </TableCell>
              <TableCell>{new Date(item.timestamp).toLocaleString("pt-BR")}</TableCell>
              <TableCell>{item.peso}</TableCell>
              <TableCell>{item.altura}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
