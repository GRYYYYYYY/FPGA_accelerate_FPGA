import com.xilinx.rapidwright.design.*;
import com.xilinx.rapidwright.device.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

/** Read-only checkpoint inspection. Never route, modify cells, or write a DCP. */
public class ClockConnectivityDump {
    static final String[] SITES={"BUFCE_ROW_FSR_X21Y6","BUFCE_LEAF_X110Y26"};
    static void row(BufferedWriter out,Object... values) throws IOException {
        for(int i=0;i<values.length;i++){
            String value=values[i]==null?"":values[i].toString();
            if(value.contains("\t")||value.contains("\n")||value.contains("\r"))throw new IOException("Non-TSV field");
            if(i>0)out.write('\t');out.write(value);
        }
        out.newLine();
    }
    static String netName(Net net){return net==null?"":net.getName();}
    static String netType(Net net){return net==null?"":net.getType().toString();}
    static void capture(String input,String output) throws Exception {
        Design.setAutoGenerateReadableEdif(false);
        Design design=Design.readCheckpoint(input);
        try(BufferedWriter out=Files.newBufferedWriter(Paths.get(output),StandardCharsets.UTF_8,StandardOpenOption.CREATE_NEW)){
            row(out,"meta","schema","rapidwright_clock_observation_v1");
            row(out,"meta","checkpoint",Paths.get(input).toAbsolutePath());
            row(out,"meta","part",design.getPartName());
            row(out,"design_counts",design.getCells().size(),design.getNets().size(),design.getSiteInsts().size());
            for(String name:SITES){
                Site site=design.getDevice().getSite(name);
                if(site==null)throw new IllegalStateException("Missing site "+name);
                SiteInst inst=design.getSiteInstFromSiteName(name);
                row(out,"site",name,site.getSiteTypeEnum(),inst==null?"absent":"present");
                if(inst!=null){
                    TreeMap<String,Net> wires=new TreeMap<>(inst.getSiteWireToNetMap());
                    for(Map.Entry<String,Net> entry:wires.entrySet())row(out,"wire_net",name,entry.getKey(),netName(entry.getValue()),netType(entry.getValue()));
                    for(SitePIP pip:inst.getSitePIPs())row(out,"site_pip",name,pip.toString(),inst.getSitePIPStatus(pip));
                    for(BEL bel:inst.getBELs()){
                        row(out,"bel",name,bel.getName(),bel.getBELType(),bel.canInvert(),bel.getInvertingPin(),bel.getNonInvertingPin());
                        for(BELPin pin:bel.getPins()){
                            Net net=inst.getNetFromSiteWire(pin.getSiteWireName());
                            row(out,"bel_pin",name,bel.getName(),pin.getName(),pin.getDir(),pin.getSiteWireName(),netName(net),netType(net),pin.isStaticSource(),pin.isGndSource(),pin.isVccSource());
                        }
                    }
                    for(Cell cell:inst.getCells()){
                        row(out,"cell",name,cell.getName(),cell.getBELName(),cell.getType(),cell.isRoutethru());
                        if(cell.getProperties()!=null)for(Map.Entry<String,com.xilinx.rapidwright.edif.EDIFPropertyValue> e:new TreeMap<>(cell.getProperties()).entrySet())row(out,"cell_property",name,cell.getName(),e.getKey(),e.getValue());
                    }
                }
                if(design.getBELAttrs()!=null){
                    SiteConfig config=design.getBELAttrs().get(site);
                    if(config!=null)for(Map.Entry<BEL,Map<String,BELAttr>> entry:config.getBELAttributes().entrySet()){
                        for(Map.Entry<String,BELAttr> attr:new TreeMap<>(entry.getValue()).entrySet()){
                            BELAttr a=attr.getValue();row(out,"bel_attribute",name,entry.getKey().getName(),attr.getKey(),a.getValue(),netName(a.getNet()),netType(a.getNet()));
                        }
                    }
                }
            }
            row(out,"complete",input);
        }
        System.out.println("CLOCK_DCP_READ_COMPLETE "+input+" -> "+output);
    }
    public static void main(String[] args) throws Exception {
        if(args.length!=4)throw new IllegalArgumentException("baseline.dcp baseline.tsv probe.dcp probe.tsv");
        capture(args[0],args[1]);capture(args[2],args[3]);
    }
}
