const dateTimeFormatter = new Intl.DateTimeFormat("ru-RU", {
  dateStyle: "medium",
  timeStyle: "short",
});


export function formatDateTime(value: string): string {
  return dateTimeFormatter.format(new Date(value));
}


export function getUserInitial(username: string): string {
  return username.trim().charAt(0).toUpperCase() || "?";
}
