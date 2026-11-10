import com.xilinx.rapidwright.design.*;
import com.xilinx.rapidwright.device.*;
import java.nio.file.*;
import java.io.*;
import java.util.*;

/** Isolated diagnostic: all selected inter-site routes cleared, one tree applied. */
public class ProbeExplicitSiteRoute {
    public static void main(String[] args) throws Exception {
        Design d=Design.readCheckpoint(args[0]);String target="cg_q[2]";
        List<PIP> selected=new ArrayList<>();
        Map<String,Net> aliases=new HashMap<>();
        for(String line:Files.readAllLines(Paths.get(args[3]))) {
            String[] x=line.split("\t");Net n=d.getNet(x[1]);
            if(n==null)continue;
            if(aliases.containsKey(x[0]) && aliases.get(x[0])!=n)throw new IllegalStateException("Ambiguous canonical net "+x[0]);
            aliases.put(x[0],n);
        }
        for(String line:Files.readAllLines(Paths.get(args[1]))) {
            String[] x=line.split("\t");
            if(x[0].equals("net")) {
                Net n=aliases.get(x[1]);
                if(n==null)throw new IllegalArgumentException("Missing physical net "+x[1]);
                n.setPIPs(Collections.emptyList());
            }
            if(x[0].equals("pip") && x[1].equals(target))selected.add(d.getDevice().getPIP(x[2]));
        }
        Net net=aliases.get(target);int through=0;
        for(PIP pip:selected) {
            if(!pip.isRouteThru())continue;
            SitePin src=pip.getStartNode().getSitePin(),dst=pip.getEndNode().getSitePin();
            if(src==null || dst==null || !src.getSite().equals(dst.getSite()))throw new IllegalStateException("Missing route-through site pins");
            SiteInst site=d.getSiteInstFromSite(src.getSite());
            if(site==null)throw new IllegalStateException("Missing site instance");
            BELPin start=src.getBELPin(site.getSiteTypeEnum());
            BELPin end=dst.getBELPin(site.getSiteTypeEnum());
            System.out.println("SITE_ENDPOINTS site="+site.getSiteName()+" type="+site.getSiteTypeEnum()+" src="+src+" dst="+dst+" start="+start+" end="+end+" net="+net);
            if(start==null || end==null || net==null)throw new IllegalStateException("Null site-route endpoint/net");
            String input=src.getPinName();
            if(!input.matches("[A-H][1-6]"))throw new IllegalStateException("Unsupported probe input");
            BEL lut=site.getBEL(input.charAt(0)+"6LUT");
            if(site.getCell(lut)!=null)throw new IllegalStateException("Probe LUT occupied");
            Cell donor=site.getCell("CARRY8");
            if(donor==null)throw new IllegalStateException("Missing donor for isolated probe");
            Cell thru=new Cell(donor.getName(),lut);
            thru.setSiteInst(site);thru.setRoutethru(true);thru.setType(donor.getType());
            thru.addPinMapping("A"+input.charAt(1),"S[6]");site.addCell(thru);
            BELPin lutIn=lut.getPin("A"+input.charAt(1)),lutOut=lut.getPin("O6");
            boolean ok=site.routeIntraSiteNet(net,lutOut,lutOut)
                && site.routeIntraSiteNet(net,lutOut,end)
                && site.routeIntraSiteNet(net,start,lutIn);
            System.out.println("EXPLICIT_SITE_ROUTE "+pip+" result="+ok+" src="+src+" dst="+dst);
            if(!ok)throw new IllegalStateException("Internal route rejected");through++;
        }
        net.setPIPs(selected);
        d.writeCheckpoint(args[2]);
        System.out.println("EXPLICIT_SITE_PROBE_COMPLETE pips="+selected.size()+" through="+through);
    }
}
