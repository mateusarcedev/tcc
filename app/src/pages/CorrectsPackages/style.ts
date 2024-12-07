import { StyleSheet } from "react-native";


export const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: '#121214',
    alignItems: 'flex-start',
    justifyContent: "flex-start",
  },
  viewChar: {
    width: "100%",
    backgroundColor: "#fff",
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    borderRadius: 5,
    padding: 12
  },
  textChart: {
    fontSize: 24,
    marginBottom: 16,
    color: "#fff"
  },
  categoriesChart: {
    flexDirection: "column",
    gap: 5
  },
  textCharts: {
    color: "#fff",
    fontSize: 32,
    marginTop: 16
  },
  table: {
    width: "100%",
    height: "50%",
    borderRadius: 5,
    marginTop: 16,
  }
});