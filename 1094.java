import java.util.Scanner;

public class Main {
	public static void main(String args[]){
		Scanner s = new Scanner(System.in);
		
		int x  = s.nextInt();
		int length = 64;
		int count = 0;
		
		while (x > 0) {
            if(length > x){
            	length /= 2;
            }
            else{
            	count++;
            	x-=length;
            }
		}
		System.out.println(count);

	}
}
