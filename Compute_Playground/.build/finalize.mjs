import fs from 'node:fs/promises';
import { pathToFileURL } from 'node:url';
const skill='C:/Users/bhavi/.codex/plugins/cache/openai-primary-runtime/presentations/26.1026.10807/skills/presentations';
const {finalizePresentation}=await import(pathToFileURL(skill+'/container_tools/artifact_tool_utils.mjs'));
const r=await finalizePresentation({workspaceDir:process.cwd(),candidatePath:process.cwd()+'/.build/extended-draft.pptx',finalPath:process.cwd()+'/docs/presentation-v2.pptx',pythonExecutable:'C:/Users/bhavi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe',integrityValidatorPath:skill+'/container_tools/inspect_presentation_package_integrity.py',layoutValidatorPath:skill+'/container_tools/inspect_presentation_layout_geometry.py',layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit'],explicitTotalSlideCount:7,materializeLiteralChartWorkbooks:true,requiredNativeChartOwnerSlides:[4],fontPolicy:{basis:'design',families:['Aptos']},verifyArtifactToolImport:true,receiptPath:process.cwd()+'/.build/presentation-v2.validation.json'});console.log(JSON.stringify(r).slice(0,1800));


