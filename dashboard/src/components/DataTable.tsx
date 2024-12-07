"use client"

import { useState, useEffect } from "react"
import axios from "axios"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"

// Define o tipo dos dados
type ProductData = {
  descricao: ReactNode
  timestamp: ReactNode
  produto_id: ReactNode
  id: string
  categoria: string
  status: string
  data: string
  peso: string
  altura: string
}

export function DataTable() {
  const [data, setData] = useState<ProductData[]>([])  // Estado para armazenar os dados
  const [loading, setLoading] = useState<boolean>(true)  // Estado de carregamento
  const [error, setError] = useState<string>("")  // Estado de erro

  useEffect(() => {
    // Função para buscar os dados da API
    const fetchData = async () => {
      try {
        const response = await axios.get("http://localhost:8000/api/ultimos_produtos")  // Atualize com o endpoint correto da sua API
        console.log(response.data)
        setData(response.data)  // Armazena os dados recebidos da API
      } catch (error) {
        setError("Erro ao carregar dados.")  // Trata erros
      } finally {
        setLoading(false)  // Atualiza o estado de carregamento para false após a requisição
      }
    }

    fetchData()
  }, [])  // Array de dependências vazio, garantindo que a requisição seja feita apenas uma vez ao montar o componente

  if (loading) {
    return <div>Carregando...</div>  // Exibe a mensagem de carregamento
  }

  if (error) {
    return <div>{error}</div>  // Exibe a mensagem de erro, se houver
  }

  return (
    <div className="bg-white p-4 rounded-lg shadow">
      <h3 className="text-lg font-semibold mb-4">Últimos Produtos Processados</h3>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>ID do produto_id</TableHead>
            <TableHead>Categoria</TableHead>
            <TableHead>Descrição</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Data e Hora</TableHead>
            <TableHead>Peso</TableHead>
            <TableHead>Altura</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.map((item, index) => (
            <TableRow key={item.produto_id || index}> {/* Fallback para o índice caso o id seja indefinido */}
              <TableCell>{item.produto_id}</TableCell>
              <TableCell>{item.categoria}</TableCell>
              <TableCell>{item.descricao}</TableCell>
              <TableCell>
                <Badge variant={item.status === "Válido" ? "secondary" : "destructive"}>
                  {item.status}
                </Badge>
              </TableCell>
              <TableCell>
                {/* Formata a data no formato pt-BR */}
                {new Date(item.timestamp).toLocaleString("pt-BR")}
              </TableCell>
              <TableCell>{item.peso}</TableCell>
              <TableCell>{item.altura}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
