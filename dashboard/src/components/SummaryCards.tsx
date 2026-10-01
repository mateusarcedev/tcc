"use client";

import { useEffect, useState } from "react";
import { CheckCircle, PackageCheck, PackageX, Boxes } from "lucide-react";

import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";

export function SummaryCards() {
  const [totalItens, setTotalItens] = useState(0);
  const [totalValidos, setTotalValidos] = useState(0);
  const [totalInvalidos, setTotalInvalidos] = useState(0);
  const [taxaSucesso, setTaxaSucesso] = useState<number | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [
          totalItensRes,
          totalValidosRes,
          totalInvalidosRes,
          taxaSucessoRes,
        ] = await Promise.all([
          api.get("/api/total_itens"),
          api.get("/api/total_validos"),
          api.get("/api/total_invalidos"),
          api.get("/api/taxa_sucesso"),
        ]);

        setTotalItens(totalItensRes.data.total_itens);
        setTotalValidos(totalValidosRes.data.total_validos);
        setTotalInvalidos(totalInvalidosRes.data.total_invalidos);
        setTaxaSucesso(taxaSucessoRes.data.taxa_sucesso);
      } catch (error) {
        console.error("Erro ao buscar dados da API", error);
      }
    };

    fetchData();
    const interval = window.setInterval(fetchData, 5000);
    return () => window.clearInterval(interval);
  }, []);

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total processado</CardTitle>
          <Boxes className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{totalItens}</div>
          <p className="text-xs text-muted-foreground">Produtos</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Produtos válidos</CardTitle>
          <PackageCheck className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{totalValidos}</div>
          <p className="text-xs text-muted-foreground">
            {totalItens > 0 ? ((totalValidos / totalItens) * 100).toFixed(1) : "0.0"}% do total
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Produtos inválidos</CardTitle>
          <PackageX className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{totalInvalidos}</div>
          <p className="text-xs text-muted-foreground">
            {totalItens > 0 ? ((totalInvalidos / totalItens) * 100).toFixed(1) : "0.0"}% do total
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Taxa de sucesso</CardTitle>
          <CheckCircle className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {taxaSucesso === null ? "—" : `${taxaSucesso}%`}
          </div>
          <p className="text-xs text-muted-foreground">Categorias aceitas</p>
        </CardContent>
      </Card>
    </div>
  );
}
