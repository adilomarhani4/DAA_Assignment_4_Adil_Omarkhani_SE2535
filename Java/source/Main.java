import java.io.*;import java.util.*;
public final class Main {
 static Object handle(Map<String,Object>x) {
  switch((String)x.get("task")) {
   case "ping": return Map.of("status","ready");
            case "lcs": return Algorithms.lcs(x);
            case "merge": return Algorithms.merge(x);
            case "tree": return Algorithms.tree(x);
            case "naive": return Algorithms.naive(x);
            case "kmp": return Algorithms.kmp(x);
            case "rk": return Algorithms.rk(x);
            case "suffix": return Algorithms.suffix(x);
            case "aho": return Algorithms.aho(x);
   default: throw new IllegalArgumentException("Unknown task");
  }
 }
 @SuppressWarnings("unchecked")
 private static Map<String,Object> parseRequest(String line) {
  return (Map<String,Object>) Json.parse(line);
 }
 public static void main(String[]args)throws Exception {
  BufferedReader r = new BufferedReader(
      new InputStreamReader(System.in, java.nio.charset.StandardCharsets.UTF_8)
  );
  String line;
  while ((line = r.readLine()) != null) {
   try {
    System.out.println(Json.write(handle(parseRequest(line))));
   } catch (UnsupportedOperationException e) {
    System.out.println(Json.write(Map.of("error", e.getMessage())));
   }
  }
 }
}
