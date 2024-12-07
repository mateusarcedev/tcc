import { Text, View } from "react-native";
import { styles } from "./style";
import { PieChart } from "react-native-gifted-charts"
import Label from "../../components/Label";
import Tabela from "../../components/Table";


export default function IncorrectsPackages() {
  const pieData = [
    { value: 54, color: '#177AD5', text: '54%' },
    { value: 30, color: '#79D2DE', text: '30%' },
    { value: 26, color: '#ED6665', text: '26%' },
  ];

  const tableHead = ['Produto', 'Horário', 'Motivo'];
  const tableData = [
    ['00596', '10:30 AM', 'Sem QR Code'],
    ['0004', '11:15 AM', 'Sem QR Code'],
    ['004947', '1:00 PM', 'Pacote de outra linha'],
    ['000049', '3:45 PM', 'Pacote de outra linha'],
    ['002', '4:30 PM', 'Sem QR Code'],
    ['00029', '5:00 PM', 'Sem QR Code'],
  ];

  return (
    <View style={styles.container}>
      <Text style={styles.textChart}>
        Resultados da semana
      </Text>
      <View style={styles.viewChar}>
        <PieChart
          donut
          showText
          textColor="black"
          innerRadius={70}
          data={pieData}
        />
        <View style={styles.categoriesChart}>
          <Label
            categoria="Celulares"
            cor="#177AD5"
          />
          <Label
            categoria="Televisores"
            cor="#79D2DE"
          />
          <Label
            categoria="Laptops"
            cor="#ED6665"
          />
        </View>
      </View>

      {/* Tabela */}
      <View style={styles.table}>
        <Tabela tableHead={tableHead} tableData={tableData} />
      </View>

    </View>
  )
}