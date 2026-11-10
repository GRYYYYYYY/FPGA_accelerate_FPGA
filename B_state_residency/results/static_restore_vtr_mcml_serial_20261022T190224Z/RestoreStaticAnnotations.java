import java.io.PrintStream;
import java.util.ArrayList;
import java.util.Map;
import com.xilinx.rapidwright.design.*;
import com.xilinx.rapidwright.design.compare.DesignComparator;
import com.xilinx.rapidwright.device.BELPin;
import com.xilinx.rapidwright.interchange.*;

/** Restore only static annotations proved to originate in the preprocessing snapshot. */
public class RestoreStaticAnnotations {
    public static void main(String[] args) throws Exception {
        if(args.length!=6)throw new IllegalArgumentException("logical original.phys preprocessed.phys routed.phys output.phys output.dcp");
        PhysNetlistReader.CHECK_CONSTANT_ROUTING_AND_NET_NAMING=false;
        PhysNetlistReader.CHECK_AND_CREATE_LOGICAL_CELL_IF_NOT_PRESENT=false;
        PhysNetlistReader.VALIDATE_MACROS_PLACED_FULLY=false;
        PhysNetlistReader.CHECK_MACROS_CONSISTENT=false;
        Design original=PhysNetlistReader.readPhysNetlist(args[1]);
        Design processed=PhysNetlistReader.readPhysNetlist(args[2]);
        Design routed=Interchange.readInterchangeDesign(args[0],args[3],null,false,null);
        int removed=0,removedPins=0;
        for(SiteInst site:routed.getSiteInsts()) {
            SiteInst before=original.getSiteInstFromSite(site.getSite());
            SiteInst baseline=processed.getSiteInstFromSite(site.getSite());
            if(before==null || baseline==null)throw new RuntimeException("Unexpected site placement");
            for(Map.Entry<String,Net> entry:new ArrayList<>(site.getSiteWireToNetMap().entrySet())) {
                String wire=entry.getKey();
                if(before.getNetFromSiteWire(wire)!=null)continue;
                Net proved=baseline.getNetFromSiteWire(wire);
                if(!entry.getValue().isStaticNet() || proved==null || !proved.isStaticNet() || !proved.getName().equals(entry.getValue().getName()))
                    throw new RuntimeException("Added wire not justified by static preprocessing snapshot: "+site.getName()+"/"+wire);
                SitePinInst pin=site.getSitePinInst(wire);
                if(pin!=null && before.getSitePinInst(wire)==null) {
                    if(!pin.getNet().isStaticNet())throw new RuntimeException("Non-static added pin");
                    pin.getNet().removePin(pin,true);removedPins++;
                }
                if(site.getNetFromSiteWire(wire)!=null) {
                    BELPin[] pins=site.getSiteWirePins(wire);
                    if(pins==null || pins.length==0)throw new RuntimeException("No wire pins for annotation");
                    site.unrouteIntraSiteNet(pins[0],pins[0]);
                }
                if(site.getNetFromSiteWire(wire)!=null)throw new RuntimeException("Static annotation remains");
                removed++;
            }
        }
        for(Net net:original.getNets()) {
            if(!net.isStaticNet() && !net.isClockNet())continue;
            Net target=routed.getNet(net.getName());
            if(target==null)throw new RuntimeException("Missing original fixed net");
            target.setPIPs(new ArrayList<>(net.getPIPs()));
        }
        PhysNetlistWriter.writePhysNetlist(routed,args[4]);
        Design reloaded=PhysNetlistReader.readPhysNetlist(args[4]);
        DesignComparator comparator=new DesignComparator();
        comparator.setComparePIPs(net->net.isStaticNet()||net.isClockNet());
        int count=comparator.compareDesigns(original,reloaded);
        try(PrintStream report=new PrintStream(args[5]+".diff.txt")){comparator.printDiffReport(report);}
        System.out.println("B_RESTORED_STATIC_ANNOTATIONS annotations="+removed+" pins="+removedPins+" differences="+count);
        if(count!=0)throw new RuntimeException("Original physical invariants differ");
        routed.writeCheckpoint(args[5]);System.out.println("B_STATIC_RESTORE_PASS");
    }
}
