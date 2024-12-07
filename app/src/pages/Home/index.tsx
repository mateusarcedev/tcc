import { StatusBar } from 'expo-status-bar';
import { Pressable, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { SafeAreaView, SafeAreaProvider, useSafeAreaInsets } from 'react-native-safe-area-context';
import CardCategory from '../../components/CardCategory';
import Television from 'react-native-vector-icons/FontAwesome';
import Smartphone from 'react-native-vector-icons/Feather';
import Package from 'react-native-vector-icons/Feather';
import Laptop from 'react-native-vector-icons/AntDesign';
import CardCharts from '../../components/CardCharts';
import { useNavigation } from '@react-navigation/native';
import Tabela from '../../components/Table';


export default function Home() {
  const navigation = useNavigation();

  const tableHead = ['Produto', 'Horário', 'Status'];
  const tableData = [
    ['00596', '10:30 AM', 'Entregue'],
    ['0004', '11:15 AM', 'Em Trânsito'],
    ['004947', '1:00 PM', 'Pendente'],
    ['000049', '3:45 PM', 'Entregue'],
    ['002', '4:30 PM', 'Em Espera'],
    ['00029', '5:00 PM', 'Cancelado'],
  ];


  return (
    <SafeAreaProvider>
      <SafeAreaView style={styles.container}>
        <StatusBar style="light" translucent />
        <Text style={styles.textCategory}>
          Top categorias
        </Text>

        <View style={styles.contentCardCategories}>
          <CardCategory
            icon={<Television name="television" size={40} color="#000" />}
          />
          <CardCategory
            icon={<Smartphone name="smartphone" size={40} color="#000" />}
          />

          <CardCategory
            icon={<Laptop name="laptop" size={40} color="#000" />}
          />
        </View>

        {/* Cards de Estatísticas */}
        <View>
          <Text style={styles.textCharts}>
            Estatísticas da Esteira
          </Text>
          <View style={styles.contentCardCharts}>
            <TouchableOpacity
              // @ts-ignore
              onPress={() => navigation.navigate('Pacotes Corretos')}
            >
              <CardCharts
                quantidade={100}
                icon={<Package name="package" size={40} color="#007205" />}
                status='Pacotes Corretos'
              />
            </TouchableOpacity>
            <TouchableOpacity
              // @ts-ignore
              onPress={() => navigation.navigate('Pacotes Incorretos')}
            >
              <CardCharts
                quantidade={20}
                icon={<Package name="package" size={40} color="#FF0000" />}
                status='Pacotes incorretos'
              />
            </TouchableOpacity>
          </View>
        </View>

        {/* Tabela */}
        <View style={styles.table}>
          <Text style={styles.textCharts}>
            Histórico do dia
          </Text>
          <Tabela tableHead={tableHead} tableData={tableData} />
        </View>


      </SafeAreaView>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#121214',
    alignItems: 'flex-start',
    justifyContent: 'flex-start',
    paddingHorizontal: 24,
    paddingVertical: 32
  },
  contentCardCategories: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    justifyContent: 'flex-start',
    gap: 10
  },
  contentCardCharts: {
    width: "100%",
    marginTop: 5,
    flexDirection: 'row',
    alignItems: 'flex-start',
    justifyContent: 'space-between',
  },
  textCategory: {
    color: "#fff",
    fontSize: 32,
    marginBottom: 8
  },
  textCharts: {
    color: "#fff",
    fontSize: 32,
    marginTop: 16
  },
  table: {
    flex: 1,
    width: "100%",
    borderRadius: 5,
  }
});
