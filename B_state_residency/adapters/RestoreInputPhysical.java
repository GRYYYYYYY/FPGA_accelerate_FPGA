import java.io.PrintStream;
import java.util.ArrayList;
import java.util.Map;
import com.xilinx.rapidwright.design.Design;
import com.xilinx.rapidwright.design.Net;
import com.xilinx.rapidwright.design.SiteInst;
import com.xilinx.rapidwright.design.SitePinInst;
import com.xilinx.rapidwright.design.compare.DesignComparator;
import com.xilinx.rapidwright.device.BELPin;
import com.xilinx.rapidwright.interchange.Interchange;
import com.xilinx.rapidwright.interchange.PhysNetlistReader;
import com.xilinx.rapidwright.interchange.PhysNetlistWriter;

/** Restore only the observed preprocessing-only CKEN annotations, with strict checks. */
public class RestoreInputPhysical {
    public static void main(String[] args) throws Exception {
        if(args.length!=5)throw new IllegalArgumentException("logical original.phys routed.phys output.phys output.dcp");
        PhysNetlistReader.CHECK_CONSTANT_ROUTING_AND_NET_NAMING=false;
        PhysNetlistReader.CHECK_AND_CREATE_LOGICAL_CELL_IF_NOT_PRESENT=false;
        PhysNetlistReader.VALIDATE_MACROS_PLACED_FULLY=false;
        PhysNetlistReader.CHECK_MACROS_CONSISTENT=false;
        Design original=PhysNetlistReader.readPhysNetlist(args[1]);
        Design routed=Interchange.readInterchangeDesign(args[0],args[2],null,false,null);
        int removed=0,removedPins=0;
        for(SiteInst site:routed.getSiteInsts()) {
            SiteInst before=original.getSiteInstFromSite(site.getSite());
            if(before==null)throw new RuntimeException("Unexpected added site");
            for(Map.Entry<String,Net> entry:new ArrayList<>(site.getSiteWireToNetMap().entrySet())) {
                String wire=entry.getKey();
                if(before.getNetFromSiteWire(wire)!=null)continue;
                if(!wire.matches("CKEN[1-4]") || !entry.getValue().isStaticNet())
                    throw new RuntimeException("Unexpected added site wire "+site.getName()+"/"+wire);
                SitePinInst pin=site.getSitePinInst(wire);
                if(pin!=null && before.getSitePinInst(wire)==null) {
                    if(!pin.getNet().isStaticNet())throw new RuntimeException("Non-static added CKEN pin");
                    pin.getNet().removePin(pin,true);removedPins++;
                }
                if(site.getNetFromSiteWire(wire)!=null) {
                    BELPin[] pins=site.getSiteWirePins(wire);
                    if(pins==null || pins.length==0)throw new RuntimeException("No wire pins for CKEN annotation");
                    site.unrouteIntraSiteNet(pins[0],pins[0]);
                }
                if(site.getNetFromSiteWire(wire)!=null)throw new RuntimeException("Could not remove preprocessing annotation");
                removed++;
            }
        }
        // Removing a SitePinInst also prunes its inter-site branch. Those are
        // original fixed static/clock stubs and must be restored verbatim.
        for(Net net:original.getNets()) {
            if(!net.isStaticNet() && !net.isClockNet())continue;
            Net target=routed.getNet(net.getName());
            if(target==null)throw new RuntimeException("Missing original fixed net");
            target.setPIPs(new ArrayList<>(net.getPIPs()));
        }
        PhysNetlistWriter.writePhysNetlist(routed,args[3]);
        Design reloaded=PhysNetlistReader.readPhysNetlist(args[3]);
        DesignComparator comparator=new DesignComparator();
        comparator.setComparePIPs(net->net.isStaticNet()||net.isClockNet());
        int count=comparator.compareDesigns(original,reloaded);
        try(PrintStream report=new PrintStream(args[4]+".diff.txt")){comparator.printDiffReport(report);}
        System.out.println("B_RESTORED_CKEN annotations="+removed+" pins="+removedPins+" differences="+count);
        if(count!=0)throw new RuntimeException("Original input invariants still differ");
        routed.writeCheckpoint(args[4]);
        System.out.println("B_RESTORE_PASS");
    }
}
