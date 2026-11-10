import com.xilinx.rapidwright.design.*;
import com.xilinx.rapidwright.edif.*;
import java.nio.file.*;
import java.io.*;
import java.util.*;

/** Logical pin demand alongside physical mapping, including explicit static nets. */
public class ExportCellPinOwnership {
    public static void main(String[] args) throws Exception {
        Design d=Design.readCheckpoint(args[0]);int count=0;
        try(BufferedWriter out=Files.newBufferedWriter(Paths.get(args[1]),StandardOpenOption.CREATE_NEW)) {
            out.write("meta\tschema\trapidwright_cell_pin_ownership_v1\n");
            for(Cell c:d.getCells()) {
                if(c.getEDIFCellInst()==null || c.getBEL()==null)continue;
                for(Map.Entry<String,String> entry:new TreeMap<>(c.getPinMappingsP2L()).entrySet()) {
                    EDIFPortInst pin=c.getEDIFCellInst().getPortInst(entry.getValue());
                    EDIFNet n=pin==null?null:pin.getNet();
                    String kind=n==null?"UNCONNECTED":n.isGND()?"GROUND":n.isVCC()?"POWER":"SIGNAL";
                    String net=n==null?"":n.getName();
                    String[] row={"pin",c.getName(),c.getSiteName(),c.getBELName(),entry.getKey(),entry.getValue(),kind,net};
                    for(String s:row)if(s.matches("(?s).*[\\t\\r\\n].*"))throw new IllegalArgumentException("Control character");
                    out.write(String.join("\t",row));out.newLine();count++;
                }
            }
            out.write("complete\t"+count+"\n");
        }
        System.out.println("CELL_PIN_OWNERSHIP_COMPLETE pins="+count);
    }
}
