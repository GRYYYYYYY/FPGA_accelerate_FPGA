import com.xilinx.rapidwright.design.Design;
import com.xilinx.rapidwright.design.SiteInst;
import com.xilinx.rapidwright.design.Net;
import com.xilinx.rapidwright.device.BELPin;
import java.nio.file.*;
import java.io.*;
import java.util.*;

/** Read-only physical intra-site ownership export; no placement/routing mutation. */
public class ExportSiteOwnership {
    static void row(BufferedWriter out, String... fields) throws IOException {
        for (String s:fields) if(s.matches("(?s).*[\\t\\r\\n].*"))
            throw new IllegalArgumentException("Control character in TSV field");
        out.write(String.join("\t",fields));out.newLine();
    }
    public static void main(String[] args) throws Exception {
        if(args.length!=2 && args.length!=3)throw new IllegalArgumentException("checkpoint output [readable_edif]");
        Design design=args.length==3?Design.readCheckpoint(args[0],args[2]):Design.readCheckpoint(args[0]);
        int wires=0,pins=0,sites=0;
        try(BufferedWriter out=Files.newBufferedWriter(Paths.get(args[1]),StandardOpenOption.CREATE_NEW)) {
            row(out,"meta","schema","rapidwright_site_ownership_v1");
            row(out,"meta","part",design.getPartName());
            List<SiteInst> ordered=new ArrayList<>(design.getSiteInsts());
            ordered.sort(Comparator.comparing(SiteInst::getSiteName));
            for(SiteInst site:ordered) {
                row(out,"site",site.getSiteName(),site.getSiteTypeEnum().name());sites++;
                Map<String,Net> ownership=new TreeMap<>(site.getSiteWireToNetMap());
                for(Map.Entry<String,Net> e:ownership.entrySet()) {
                    row(out,"wire",site.getSiteName(),e.getKey(),e.getValue().getName());wires++;
                    BELPin[] belPins=site.getSiteWirePins(e.getKey());
                    if(belPins==null)continue;
                    for(BELPin pin:belPins) {
                        row(out,"bel_pin",site.getSiteName(),pin.getBELName(),pin.getName(),e.getValue().getName());pins++;
                    }
                }
            }
            row(out,"complete",Integer.toString(sites),Integer.toString(wires),Integer.toString(pins));
        }
        System.out.println("SITE_OWNERSHIP_COMPLETE sites="+sites+" wires="+wires+" pins="+pins);
    }
}
