import { StyleSheet } from "react-native";

export const styles = StyleSheet.create({
  container: {
    width: 170,
    height: 170,
    borderRadius: 5,
    padding: 5,
    alignItems: 'center',
    justifyContent: "space-between",
    backgroundColor: '#fff',
  },
  header: {
    flexDirection: "row",
    width: "100%",
    alignItems: "center",
    justifyContent: "space-between"
  },
  quantity: {
    fontSize: 32,
    fontWeight: "bold"
  },
  status: {
    fontSize: 14,
    fontWeight: "400",
    marginBottom: 5
  },
});