import { Charts } from "@/components/Charts";
import { DataTable } from "@/components/DataTable";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { SummaryCards } from "@/components/SummaryCards";


export default function Home() {
  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <SummaryCards />
        <div className="mt-8">
          <Charts />
        </div>
        <div className="mt-8">
          <DataTable />
        </div>
      </main>
      <Footer />
    </div>
  )
}

