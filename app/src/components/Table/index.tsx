import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Table, Row, Rows } from 'react-native-reanimated-table';

interface TabelaProps {
  tableHead: string[];
  tableData: string[][];
}

const Tabela: React.FC<TabelaProps> = ({ tableHead, tableData }) => {
  return (
    <View style={styles.container}>
      <View style={styles.tableContainer}>
        <Table borderStyle={{ borderWidth: 2, borderColor: '#0002' }}>
          <Row data={tableHead} style={styles.head} textStyle={styles.text} />
          <Rows data={tableData} textStyle={styles.text} />
        </Table>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 8,
    backgroundColor: '#fff',
    borderRadius: 5,
  },
  tableContainer: {
    flex: 1, // Para ocupar o restante da tela
    width: '100%', // Largura da tabela
    alignSelf: 'center',
  },
  head: {
    height: 40,
    backgroundColor: '#f1f8ff', // Cor de fundo do cabeçalho
  },
  text: {
    margin: 6,
    textAlign: 'center', // Centraliza o texto
  },
});

export default Tabela;
