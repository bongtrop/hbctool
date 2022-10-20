
# Process

create a fork of repository https://github.com/cyfinoid/hbctool 

## Example adding HBC89

1. update `hbctool/hbc/__init__.py` 
![image](https://user-images.githubusercontent.com/236843/197051405-6cc73905-c3ff-4624-b7ce-d566b6d22e4b.png)

2. Create a folder HBC89 in `hbctool/hbc/` folder
3. Perform following actions
	1. `mkdir data raw tool`
	2. `cp ../hbc76/translator.py ./` 
	3. `cp ../hbc76/parser.py ./`
	4. `cd tool; cp ../../hbc76/tool/opcode_generator.py; cd ..`
	5. `cp ../hbc76/data/structure.json ./data/structure.json`
4. Find the exact version of hermes which creates same bytecode version
For latest versions of facebook hermes after version 0.70 hermes is compiled by facebook reactnative team directly and we need to dig in to identify the source.

a. we used reactnative 0.70.3 as our base.
b. Either download the source corresponding to that version or navigate it in the github interface itself. https://github.com/facebook/react-native/blob/v0.70.3/sdks/.hermesversion 
b. under `sdks/.hermesversion` contains tag details for the specific hermes code used in this version of reactnative.
c. In our case we found `hermes-2022-09-14-RNv0.70.1-2a6b111ab289b55d7b78b5fdf105f466ba270fd7`

Now navigate to facebook/hermes https://github.com/facebook/hermes
there is a same name tag in that project https://github.com/facebook/hermes/tree/hermes-2022-09-14-RNv0.70.1-2a6b111ab289b55d7b78b5fdf105f466ba270fd7

**Please note**: earlier notice from original author @ https://suam.wtf/posts/react-native-application-static-analysis-en/ suggested to look for Version as `The version of Hermes bytecode can be found in /include/hermes/BCGen/HBC/BytecodeFileFormat.h file around line 33.`
However the new updates have pushed version number out in a seperate file @ `include/hermes/BCGen/HBC/BytecodeVersion.h`

we need the content on this project for next step.

5. Download following files from that location into raw folder from `include/hermes/BCGen/HBC/` folder of the project tree at that specific trunk
6. add `BytecodeList.def`  https://github.com/facebook/hermes/blob/hermes-2022-09-14-RNv0.70.1-2a6b111ab289b55d7b78b5fdf105f466ba270fd7/include/hermes/BCGen/HBC/BytecodeList.def 
7. add `BytecodeFileFormat.h` https://github.com/facebook/hermes/blob/hermes-2022-09-14-RNv0.70.1-2a6b111ab289b55d7b78b5fdf105f466ba270fd7/include/hermes/BCGen/HBC/BytecodeFileFormat.h 
8. add `SerializedLiteralGenerator.h` https://github.com/facebook/hermes/blob/hermes-2022-09-14-RNv0.70.1-2a6b111ab289b55d7b78b5fdf105f466ba270fd7/include/hermes/BCGen/HBC/SerializedLiteralGenerator.h 

Once these 3 files are copied then you run the opcode generator tool in `tool` folder.
9. `cd tool;  python3 opcode_generator.py` This will generate the `opcode.json` in `data` folder

Once this is done we just need one more change. copy over `__init__.py` from older version of hbcXX and we modify 2 lines.
Class name to match HBCXX and change getVersion(self) value
![image](https://user-images.githubusercontent.com/236843/197051569-df72e045-8a56-4773-b46f-50f997a17877.png)


Note: 
This is still work in progress, we are working backwards from the code. I need to double check if there are other changes then just this needed.
