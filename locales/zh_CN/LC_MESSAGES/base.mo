Þ    .        =   ü      ð     ñ     þ               !     2  7   F  £   ~  <   "     _  +   |  [   ¨  ø     -   ý  s   +          ´  /   Ã     ó     {  y     %   	     '	     :	     B	     Ú	     ç	  
   ý	     
  G   
     Ü
  T   ü
  S   Q  D   ¥     ê     ý  '        9     I     X     s          ¨  j   8     £    #     6  
   >     I  
   W     b     p  6        À  3   X       (   «  9   Ô  ¢        ±  N   Ð          ,     9  i   X     Â  W   Ï     '     F     X  t   `     Õ     Ü     ì  z   ù  3   t     ¨  =   Ä  ?     *   B     m       !        ±     ¾  !   Ô     ö     	  v   "  9     f   Ó                       "            #                    .      -         '          )   (      $   
                +      !   	             &                    ,          %         *                                  Calculation  Loading  Sample Selection  Saving  Stretch Options 1.
Load your image. 2.
Stretch your image if necessary to reveal gradients. 3.
Select background points
  a) manually with left click
  b) automatically via grid (grid selection)
You can remove already set points by right clicking on them. 4.
Click on Calculate Background to get the processed image. 5.
Save the processed image. A newer version of GraXpert is available at Adjust the number of points per row for the grid created by automatic background selection. Adjust the smoothing parameter for the interpolation method. A too small smoothing parameter may lead to over- and undershooting inbetween background points, while a too large smoothing parameter may not be suited for large deviations in gradients. An error occurred while loading your picture. Automatically stretch the picture to make gradients more visible. The saved pictures are unaffected by the stretch. Calculate Background Calculating... Choose between different interpolation methods. Choose the bitdepth of the saved pictures and the file format. If you are working with a .fits image the fits header will be preserved. Create Grid Creates a grid with the specified amount of points per row and rejects points below a threshold defined by the tolerance. Error occurred when saving the image. Grid Tolerance: {} H
E
L
P If enabled, additional grid points are automatically created based on 1) the luminance of the sample just added and 2) the grid tolerance slider below. Instructions Interpolation Method: Load Image Load your image you would like to correct. 

Supported formats: .tiff, .fits, .png, .jpg 
Supported bitdepths: 16 bit integer, 32 bit float Please load your picture and select background points with right click. Please load your picture first. Please select at least 16 background points with right click for the Splines method. Please select at least 2 background points with right click for the Kriging method. Please select background points and press the Calculate button first Points per row: {} Reset Sample Points Reset all the chosen background points. Save Background Save Processed Save Stretched & Processed Save the background model Save the processed picture Switch display between 

Original: Your original picture 
Processed: Picture with subtracted background model 
Background: The background model The tolerance adjusts the threshold for rejection of background points with automatic background selection Use the specified interpolation method to calculate a background model and subtract it from the picture. This may take a while. Project-Id-Version: PACKAGE VERSION
PO-Revision-Date: 2022-04-15 13:57+0200
Last-Translator: Automatically generated
Language-Team: none
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Generated-By: pygettext.py 1.5
Language: zh_CN
  è®¡ç®  å è½½ä¸­  æ ·æ¬éæ©  ä¿å­ä¸­  æä¼¸éé¡¹ 1.
å è½½æ¨çå¾åã 2.
å¦æå¿è¦ï¼æä¼¸æ¨çå¾åä»¥æ¾ç¤ºæ¸åã 3.
éæ©èæ¯ç¹
  a) å·¦é®æå¨éæ©
  b) éè¿ç½æ ¼èªå¨éæ©ï¼ç½æ ¼éæ©ï¼
æ¨å¯ä»¥éè¿å³é®ç¹å»å·²è®¾ç½®çç¹æ¥ç§»é¤å®ä»¬ã 4.
ç¹å»è®¡ç®èæ¯ä»¥è·åå¤çåçå¾åã 5.
ä¿å­å¤çåçå¾åã ææ°ç GraXpert å¯ç¨ï¼ä¸è½½å°å è°æ´èªå¨èæ¯éæ©åå»ºçç½æ ¼çæ¯è¡ç¹æ°ã è°æ´æå¼æ¹æ³çå¹³æ»åæ°ãå¹³æ»åæ°è¿å°å¯è½å¯¼è´èæ¯ç¹ä¹é´çè¿å²åæ¬ å²ï¼èå¹³æ»åæ°è¿å¤§å¯è½ä¸éåæ¸åä¸­çå¤§åå·®ã å è½½å¾çæ¶åçéè¯¯ã èªå¨æä¼¸å¾çä»¥ä½¿æ¸åæ´ææ¾ãä¿å­çå¾çä¸åæä¼¸å½±åã è®¡ç®èæ¯ è®¡ç®ä¸­... éæ©ä¸åçæå¼æ¹æ³ã éæ©ä¿å­å¾åçä½æ·±åæä»¶æ ¼å¼ãå¦ææ¨å¤ççæ¯ .fits å¾åï¼fits å¤´å°è¢«ä¿çã åå»ºç½æ ¼ åå»ºå·ææå®æ¯è¡ç¹æ°çç½æ ¼ï¼å¹¶æç»ä½äºå®¹å·®å®ä¹çéå¼çç¹ã ä¿å­å¾åæ¶åçéè¯¯ã ç½æ ¼å®¹å·®ï¼{} å¸®
å© å¦æå¯ç¨ï¼éå ç½æ ¼ç¹å°åºäº 1) åæ·»å æ ·æ¬çäº®åº¦å 2) ä¸é¢çç½æ ¼å®¹å·®æ»åèªå¨åå»ºã è¯´æ æå¼æ¹æ³ï¼ å è½½å¾å å è½½æ¨è¦æ ¡æ­£çå¾åã 

æ¯æçæ ¼å¼ï¼ .tiff, .fits, .png, .jpg 
æ¯æçä½æ·±ï¼16 ä½æ´æ°, 32 ä½æµ®ç¹ è¯·å è½½æ¨çå¾çå¹¶ç¨å³é®éæ©èæ¯ç¹ã è¯·åå è½½æ¨çå¾çã è¯·ç¨å³é®éæ©è³å° 16 ä¸ªèæ¯ç¹ç¨äºæ ·æ¡æ¹æ³ã è¯·ç¨å³é®éæ©è³å° 2 ä¸ªèæ¯ç¹ç¨äºåééæ¹æ³ã è¯·åéæ©èæ¯ç¹å¹¶æä¸è®¡ç®æé® æ¯è¡ç¹æ°ï¼{} éç½®æ ·æ¬ç¹ éç½®ææéæ©çèæ¯ç¹ã ä¿å­èæ¯ ä¿å­å¤çåå¾å ä¿å­æä¼¸åå¤çåçå¾å ä¿å­èæ¯æ¨¡å ä¿å­å¤çåçå¾å å¨ä»¥ä¸æ¾ç¤ºä¹é´åæ¢

åå§ï¼æ¨çåå§å¾ç
å¤çåï¼åå»èæ¯æ¨¡åçå¾ç
èæ¯ï¼èæ¯æ¨¡å å®¹å·®è°æ´èªå¨èæ¯éæ©æ¶èæ¯ç¹çæç»éå¼ ä½¿ç¨æå®çæå¼æ¹æ³è®¡ç®èæ¯æ¨¡åå¹¶ä»å¾åä¸­åå»å®ãè¿å¯è½éè¦ä¸æ®µæ¶é´ã 