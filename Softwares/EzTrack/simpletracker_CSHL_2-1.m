%% EZTrack
% Original script written by Andreas Braun (andreas.braun_at_crg.eu)
% Modified by Matthieu Louis (mlouis_at_crg.eu) and Ajinkya Deogade (ajinkya.deogade_at_crg.eu)
% Purpose: basic script aiming at tracking a single larva freely moving in a Petri
% dish

% Instructions: run this programm in the folder that contains the image
% sequence to be analyzed. This routine requires the image analysis package
% of Matlab.

close all
clear all
warning off
addpath(pwd)

%% INITILIAZE TRACKER: Set parameters of the tracker
radius_mm=44; %inner diameter of regular petri dish is 88 mm
fps=input('ENTER THE FRAME RATE OF THE CAPTURED IMAGE SEQUENCE (1/s): ');
intensity_threshold=0.4; % threshold for binary image conversion; set to 0.5 in absence of lid; set to 0.4 in presence of the lid
highRes_flag=0; %set to 1 to enable high resolution analysis with opening and closing of the blobs, set to 0 otherwise
edge_tolerance=5; % in mm, minimal distance between animal and wall of dish

% Path to folder containing image sequences
cd('/Volumes/CRG/CSHL_2016_Softwares/ezTrack/Data/2016-07-13-22-35-17/')

%% READING IMAGES: Load the image files
filesArray=dir('TL_image_*.jpg');
% filesArray contains list of all files names.
% Note that the frame rate can be reduced by
% hopping between entries of the filesArray
filename=filesArray(1).name; %% Read first image file name
image=imread(filename); %% Load first image file

%% INITIALIZE ARENA: Set parameters of the arena (odor source, initial larvae position, arena size)
figure;
imshow(image) %% Show first image file for annotation
% Mark the dishcentroid
title('MARK CENTER OF ODOR/LIGHT SOURCE')
set(gca,'xtick',[],'ytick',[])
[sourceCentroidx,sourceCentroidy]=ginput(1); %% Store source location
% Mark the dishcentroid
clf
imshow(image)
title('MARK CENTER OF DISH')
set(gca,'xtick',[],'ytick',[])
[dishCentroidx,dishCentroidy]=ginput(1);
% Mark the edge of the dish
clf
imshow(image)
title('MARK POINT AT THE BORDER OF DISH (FOR CALCULATION OF RADIUS)')
set(gca,'xtick',[],'ytick',[])
[borderx,bordery]=ginput(1);
% Calculate arena radius in pixels
deltax=abs(borderx-dishCentroidx);
deltay=abs(bordery-dishCentroidy);
radius=sqrt(deltax^2+deltay^2);
%calculate scaling_factor mm/pixel
scaling_factor=radius_mm/radius;

%% Main Tracking Routine
for frameNumber=1:1:length(filesArray)
    
    %load image
    filename=filesArray(frameNumber).name;
    current_image=imread(filename);
    %bw=im2bw(current_image, intensity_threshold);
    bw=im2bw(current_image, graythresh(current_image));
    
    % im2bw: This function converts the input image into a B&W image that is then
    % thresholded
    % intensity_threshold: Threshold used to convert the image into black and
    % white. Set this parameter to 0.5 (level) to adjust the sensitivity of tracker.
    % Increase in contrast can be obtained by making the threshold higher.
    
    if frameNumber==1;
        % Compute Background Image: sum over all images to generate average image used for backgorund
        %subtraction
        for file_index=1:length(filesArray)
            filename=filesArray(file_index).name;
            temp_image=imread(filename);
            if file_index==1
                totalimage=temp_image;
            else
                totalimage=double(totalimage)+double(temp_image);
            end
        end
        %average image
        avimage=uint8(totalimage/length(filesArray)); % Converts background image to unsigned 8-bit integer
        %av_picBW=im2bw(avimage,intensity_threshold); % Threshold background image based on the level given as second argument
        av_picBW=im2bw(avimage,graythresh(avimage)); % Threshold background image based on the level given as second argument
        
        
        imshow(avimage);
        %pause
        
        clf
        first_image=image;
        imshow(image)
        title('TAG THE LARVA (CLICK ON ITS CENTER)')
        set(gca,'xtick',[],'ytick',[])
        [centroidx(frameNumber),centroidy(frameNumber)]=ginput(1);
        sourcedistx(frameNumber)=centroidx(frameNumber)-dishCentroidx;
        sourcedisty(frameNumber)=centroidy(frameNumber)-dishCentroidy;
        DIST(frameNumber)=sqrt(sourcedistx(frameNumber).^2+sourcedisty(frameNumber).^2);
        DISH_CENTER_DIST_MM(frameNumber)=DIST(frameNumber)*scaling_factor;
        
    end
    
    %% Image Processing to Extract Larva
    % Identification of initial position of the larva (detection of
    % corresponding blob)
    % image subtraction
    %current_picBW=im2bw(current_image,intensity_threshold); % converts image to binary image by thresholding
    current_picBW=im2bw(current_image,graythresh(current_image)); % previous with addition from Daeyeon
    current_picWB_sub=imabsdiff(current_picBW,av_picBW);
    %threshold blob size
    current_picWB_sub=bwareaopen(current_picWB_sub,10); %this parameter can be tweaked as well: 10 pixels is used here as a threshold on blobs. When larva reaches the wall, the blob might become too small to be detected.
    if isempty(current_picWB_sub)
        error('No blob detected')
    end
    
    % Plot for control purposes
    if frameNumber==2 && highRes_flag==1
        clf
        subplot(2,3,1)
        imshow(current_image);
        title('Raw image')
        
        subplot(2,3,2)
        imshow(av_picBW);
        title('Background image')
        
        subplot(2,3,3)
        imshow(current_picWB_sub);
        title('Subtracted image')
        
    end
    
    %%
    % Subroutine implementing opening and closing of blobs to improve
    % quality of larva's reconstruction
    if highRes_flag==1
        % Subroutine smoothening the blob corresponding to the larva
        se = strel('diamond', 2); % definition of structuring element (filter)
        current_picWB_sub=imdilate(current_picWB_sub,se); %dilate: makes blob bigger
        %
        if frameNumber==2 && highRes_flag==1
            subplot(2,3,4)
            imshow(current_picWB_sub);
            title('Dilated image')
        end
        
        current_picWB_sub=imfill(current_picWB_sub,'holes');
        %
        if frameNumber==2 && highRes_flag==1
            subplot(2,3,5)
            imshow(current_picWB_sub);
            title('Filled image')
        end
        
        se = strel('diamond',2);
        current_picWB_sub=imerode(current_picWB_sub,se); %reduction in size of larva, but gain in smoothness
        %
        if frameNumber==2 && highRes_flag==1
            subplot(2,3,6)
            imshow(current_picWB_sub);
            title('Eroded image')
        end
    end
    %%
    
    % Subroutine implementing blob detection
    [X,noise]=bwlabel(current_picWB_sub,8); %labels connected components of the binary image
    noisedata=regionprops(X,'basic'); % Compute basic properties of components
    allsortnoiseareas=[noisedata.Area]; % Define size of blobs, not used in present version
    allnoisecentroids=[noisedata.Centroid]; %centroid of blobs
    sortnoiseareas=sort(allsortnoiseareas,'descend');
    
    dist=[];
    if frameNumber>1
        % tracking based on proximity rule
        for i=1:length(sortnoiseareas) %compute distance between every blob and previous position of larva
            xdist=centroidx(frameNumber-1)-allnoisecentroids(i*2-1);
            ydist=centroidy(frameNumber-1)-allnoisecentroids(i*2);
            dist(i)=sqrt(xdist^2+ydist^2); %another threshold can be added here (wil depend on frame rate)
        end
        
        mindist=min(dist);
        minpos=find(dist==mindist);
        centroidx(frameNumber)=allnoisecentroids(minpos*2-1);
        centroidy(frameNumber)=allnoisecentroids(minpos*2);
        %
        sourcedistx(frameNumber)=centroidx(frameNumber)-dishCentroidx;
        sourcedisty(frameNumber)=centroidy(frameNumber)-dishCentroidy;
        DIST(frameNumber)=sqrt(sourcedistx(frameNumber).^2+sourcedisty(frameNumber).^2);
        DISH_CENTER_DIST_MM(frameNumber)=DIST(frameNumber)*scaling_factor;
        %
        last_k=frameNumber;
    end
    
    % End analysis if distance to wall is smaller than parameter edge_tolerance
    if DISH_CENTER_DIST_MM(frameNumber)>(radius_mm-edge_tolerance)
        display('Wall contacted before end of trajectory')
        break
    end
    
end

%optional ploting routine
figure;
imshow(current_picWB_sub);
hold on
plot(centroidx,centroidy,'w')
scatter(dishCentroidx,dishCentroidy,40,'ro','filled')
scatter(sourceCentroidx,sourceCentroidy,40,'bo','filled')
circle([dishCentroidx,dishCentroidy],radius,5000,'w-');
axis equal

%ANALYSIS
CENTROIDX_MM=centroidx*scaling_factor;
CENTROIDY_MM=centroidy*scaling_factor;
%compute distance to dishcentroid
xdist=centroidx-dishCentroidx;
ydist=centroidy-dishCentroidy;
DISH_CENTER_DIST_MM=DIST*scaling_factor;
%compute distance to source in pixels and convert it into mm
sourcedistx=centroidx-sourceCentroidx;
sourcedisty=centroidy-sourceCentroidy;
SOURCEDIST=sqrt(sourcedistx.^2+sourcedisty.^2);
SOURCEDISH_CENTER_DIST_MM=SOURCEDIST*scaling_factor;

time=(1/fps:1/fps:last_k/fps);
figure;
plot(time,SOURCEDISH_CENTER_DIST_MM,'LineWidth',2,'color','blue');
hold on
plot(time,DISH_CENTER_DIST_MM,'LineWidth',2,'color','red');
legend('Distance to source','Distance to center of dish')
title('Distance to source and center of dish (mm)')
xlabel('Time (s)');
ylabel('Distance (mm)');

save CENTROIDX_MM CENTROIDX_MM;
save CENTROIDY_MM CENTROIDY_MM;
save DISH_CENTER_DIST_MM DISH_CENTER_DIST_MM;
save SOURCEDISH_CENTER_DIST_MM SOURCEDISH_CENTER_DIST_MM;