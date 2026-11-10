"""Prepare verification-only CP port monitoring; does not launch a simulation."""
import hashlib
import json
import sys
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def instrument(original):
    declaration = "module tb_candidate_offer;"
    marker = ' $display("FOURTH_WARM_PASS polls=83 expands=82 candidates=402 costs=231");'
    assert original.count(declaration) == original.count(marker) == 1
    assert original.count("\nendmodule") == 1
    assert "ce_cycles" not in original
    counters = """
 integer ce_cycles=0,ce_safe=0,ce_edit=0,ce_busy=0;
 integer ce_requests=0,ce_replies=0,ce_imports=0,ce_exports=0;
"""
    monitor = """
 always @(posedge clk)if(!k_cold_rst)begin
  if((^{system.controller.cp_safe,system.controller.host_label_edit})===1'bx)
   $fatal(1,"checkpoint native safe/edit unknown");
  if(system.controller.cp_safe&&system.controller.host_label_edit)
   $fatal(1,"checkpoint native safe/edit overlap");
  ce_cycles=ce_cycles+1;
  if(system.controller.cp_safe)ce_safe=ce_safe+1;
  if(system.controller.host_label_edit)ce_edit=ce_edit+1;
  if(system.controller.cp_busy)ce_busy=ce_busy+1;
  if(system.controller.cp_valid&&system.controller.cp_ready)ce_requests=ce_requests+1;
  if(system.controller.cp_rsp_valid&&system.controller.cp_rsp_ready)ce_replies=ce_replies+1;
  if(system.controller.cp_s_valid&&system.controller.cp_s_ready)ce_imports=ce_imports+1;
  if(system.controller.cp_m_valid&&system.controller.cp_m_ready)ce_exports=ce_exports+1;
 end
"""
    finish = """ if(ce_cycles==0||ce_safe==0||ce_busy==0||ce_requests==0||ce_requests!=ce_replies||ce_imports==0||ce_exports==0)
  $fatal(1,"checkpoint native coverage missing or unbalanced");
 $display("CHECKPOINT_EDIT_EXCLUSION_PASS cycles=%0d safe=%0d edit=%0d busy=%0d requests=%0d replies=%0d imports=%0d exports=%0d",ce_cycles,ce_safe,ce_edit,ce_busy,ce_requests,ce_replies,ce_imports,ce_exports);
"""
    return original.replace(declaration, declaration+counters).replace(
        "\nendmodule", monitor+"\nendmodule").replace(marker, finish+marker)


if __name__ == "__main__":
    reference, output = map(lambda x: Path(x).resolve(), sys.argv[1:])
    manifest = json.loads((reference/"manifest.json").read_text())
    assert manifest["status"] == "observed"
    source = reference/"sources/tb_query_fault.sv"
    assert sha(source) == manifest["sources"]["tb_query_fault.sv"]["sha256"]
    text = instrument(source.read_text())
    assert not output.exists()
    output.mkdir()
    target = output/"tb_query_fault.sv"
    target.write_text(text)
    (output/"manifest.json").write_text(json.dumps(dict(
        status="prepared_not_compiled_or_simulated",
        reference=str(reference), reference_manifest_sha256=sha(reference/"manifest.json"),
        original_tb_sha256=sha(source), monitored_tb_sha256=sha(target),
        generator_sha256=sha(Path(__file__)),
        scope="Verification only. Actual CP ports; safe/edit unknown and overlap fatal. "
              "Requires nonzero safe/busy/import/export and balanced command replies. "
              "Edit count reported without assuming this fixture exercises ordinary edits. "
              "No RTL change, functional pass, timing result or automatic submission."
    ), indent=2)+"\n")
