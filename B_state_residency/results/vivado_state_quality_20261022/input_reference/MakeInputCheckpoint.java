import com.xilinx.rapidwright.design.Design;
import com.xilinx.rapidwright.interchange.Interchange;
public class MakeInputCheckpoint { public static void main(String[] a) throws Exception {
 Design d=Interchange.readInterchangeDesign(a[0],a[1],null,false,null);d.writeCheckpoint(a[2]);
}}