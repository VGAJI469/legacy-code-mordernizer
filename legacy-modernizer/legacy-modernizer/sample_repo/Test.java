// This is a legacy system
// TODO: optimize later
// Author: unknown

public class Test {

    // Main entry point
    public static void main(String[] args) {
        int result = calculateSum(5, 10); // calculate result
        System.out.println(result);
    }

    /* Multi-line comment
       explaining business logic
       which is outdated */

    public static int calculateSum(int a, int b) {
        return add(a, b); // call helper
    }

    public static int add(int x, int y) {
        return x + y; // simple addition
    }

    // DEAD FUNCTION - not used
    public static int unusedFunction(int a) {
        return a * 2;
    }
}