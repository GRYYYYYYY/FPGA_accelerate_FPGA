import com.xilinx.rapidwright.design.Design;
import java.nio.file.*;

public class RoundTripBaseline {
    public static void main(String[] args) {
        if(Files.exists(Paths.get(args[1])))throw new IllegalArgumentException("Existing output");
        Design d=Design.readCheckpoint(args[0]);
        d.writeCheckpoint(args[1]);
        System.out.println("UNMODIFIED_BASELINE_ROUNDTRIP_COMPLETE");
    }
}
