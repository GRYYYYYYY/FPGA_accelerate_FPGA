import com.xilinx.rapidwright.design.Design;
import com.xilinx.rapidwright.device.PIP;
import com.xilinx.rapidwright.router.RouteThruHelper;
import java.nio.file.*;
import java.io.*;

/** Existing RapidWright fixed-design check, exported as evidence, not certification. */
public class ExportRouteThruAvailability {
    public static void main(String[] args) throws Exception {
        Design d=Design.readCheckpoint(args[0]);int count=0;
        try(BufferedWriter out=Files.newBufferedWriter(Paths.get(args[2]),StandardOpenOption.CREATE_NEW)) {
            out.write("meta\tschema\trapidwright_route_thru_availability_v1\n");
            for(String line:Files.readAllLines(Paths.get(args[1]))) {
                String[] f=line.split("\t");if(!f[0].equals("pip"))continue;
                PIP pip=d.getDevice().getPIP(f[1]);
                if(pip==null)throw new IllegalArgumentException("Missing PIP "+f[1]);
                String result;
                try { result=RouteThruHelper.isRouteThruPIPAvailable(d,pip)?"available":"unavailable"; }
                catch(RuntimeException e) {result="unsupported:"+e.getClass().getSimpleName();}
                out.write("pip\t"+f[1]+"\t"+pip.isRouteThru()+"\t"+result+"\n");count++;
            }
            out.write("complete\t"+count+"\n");
        }
        System.out.println("ROUTE_THRU_AVAILABILITY_COMPLETE pips="+count);
    }
}
