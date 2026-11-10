import com.xilinx.rapidwright.design.Design;
import com.xilinx.rapidwright.design.compare.DesignComparator;
import com.xilinx.rapidwright.interchange.PhysNetlistReader;
public class ComparePhysical {
 public static void main(String[] args) throws Exception {
  PhysNetlistReader.CHECK_CONSTANT_ROUTING_AND_NET_NAMING=false;
  PhysNetlistReader.CHECK_AND_CREATE_LOGICAL_CELL_IF_NOT_PRESENT=false;
  PhysNetlistReader.VALIDATE_MACROS_PLACED_FULLY=false;
  PhysNetlistReader.CHECK_MACROS_CONSISTENT=false;
  Design a=PhysNetlistReader.readPhysNetlist(args[0]),b=PhysNetlistReader.readPhysNetlist(args[1]);
  DesignComparator c=new DesignComparator();c.setComparePIPs(n -> n.isStaticNet() || n.isClockNet());
  int count=c.compareDesigns(a,b);c.printDiffReport(System.out);
  System.out.println("B_DELTA_DIFFERENCES="+count);
  if(count!=0)throw new RuntimeException("Physical delta outside signal PIPs");
 }
}
