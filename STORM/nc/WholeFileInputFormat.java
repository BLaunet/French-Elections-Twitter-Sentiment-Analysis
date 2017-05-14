package nc;

import java.io.IOException;
import java.util.List;
import java.util.ArrayList;

import ucar.nc2.NetcdfFile;
import ucar.nc2.Variable;
import ucar.ma2.*;

import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.fs.Path;  
import org.apache.hadoop.io.NullWritable;  
import org.apache.hadoop.io.FloatWritable;   
import org.apache.hadoop.mapreduce.JobContext; 
import org.apache.hadoop.mapreduce.InputSplit;  
import org.apache.hadoop.mapreduce.RecordReader;  
import org.apache.hadoop.mapreduce.TaskAttemptContext;  
import org.apache.hadoop.mapreduce.lib.input.FileSplit;  

public class WholeFileInputFormat extends FileInputFormat<NullWritable, FloatArrayWritable> {
	
	@Override
	protected boolean isSplitable(JobContext context, Path file) {
		return false;
		
	}

	@Override
	public RecordReader<NullWritable, FloatArrayWritable> createRecordReader(InputSplit split, TaskAttemptContext context) 
			throws IOException, InterruptedException {
		
		WholeFileRecordReader reader = new WholeFileRecordReader();
		reader.initialize(split, context);
		return reader;
	}

	class WholeFileRecordReader extends RecordReader<NullWritable, FloatArrayWritable> {
		
		private FileSplit fileSplit;
		private FloatArrayWritable value = new FloatArrayWritable();
		private float processed = 0F;
	
		private NetcdfFile dataFile = null;
		private Variable dataVar = null;
		private int[] shape;
		private List<Range> ranges = null;
		private int frames = 0;
		private int atoms = 0;
		private int spatial = 0;
		private int currentFrame = 0;
	
		@Override
		public void initialize(InputSplit split, TaskAttemptContext context)
				throws IOException, InterruptedException {
			
			this.fileSplit = (FileSplit) split;
			
			String file = fileSplit.getPath().toString();
			System.out.println("reading from " + file);
			
			try {
				dataFile = NetcdfFile.open(file);
				dataVar = dataFile.findVariable("coordinates");
				
				if (dataVar == null) {
					System.out.println("Cant find Variable coordinates");
					throw new IOException("Cant find Variable coordinates");
				}
				shape = dataVar.getShape();
				
				// ranges[0] = frames (3626065)
				// ranges[1] = atoms (1242)
				// ranges[2] = spatial (3)
				ranges = dataVar.getRanges();
				frames = ranges.get(0).length();
				atoms = ranges.get(1).length();
				spatial = ranges.get(2).length();

				System.out.println("number of frames:" + frames);
				System.out.println("number of atoms:" + atoms);
				System.out.println("spatial:" + spatial);
				
			} catch (java.io.IOException e) {
				e.printStackTrace();    
			} 
			
		}

		@Override
		public boolean nextKeyValue() throws IOException, InterruptedException {
			
			if (currentFrame >= frames)
				return false;
		    ArrayFloat.D3 dataArray;
		    
		    try {
		        Range frameRange = new Range(currentFrame, currentFrame);
		        Range atomRange = new Range(0, atoms - 1);
		        Range spatialRange = new Range(0, spatial - 1);
		        ArrayList<Range> l = new ArrayList<Range> ();
		        l.add(frameRange);
		        l.add(atomRange);
		        l.add(spatialRange);
		        dataArray = (ArrayFloat.D3) dataVar.read(l);
		        float[] f = (float[])dataArray.copyTo1DJavaArray();
		        FloatWritable[] faw = new FloatWritable[f.length];
		        for (int i = 0; i < f.length; i++) {
		        	FloatWritable fw = new FloatWritable();
		        	fw.set(f[i]);
		        }
		        
		        value.set(faw);
		        
		        currentFrame++;
		        
		        processed = (float)currentFrame / (float)frames;
		    
		    } catch (InvalidRangeException e) {
		    	e.printStackTrace();
		    }
		return true;
		}
		
		@Override
		public NullWritable getCurrentKey() throws IOException, InterruptedException {
			return NullWritable.get();
		}
		
		@Override
		public FloatArrayWritable getCurrentValue() throws IOException, InterruptedException {
			return value;
		}
		
		@Override
		public float getProgress() throws IOException {
			return processed;
		}
		
		@Override
		public void close() throws IOException {
			
			if (dataFile != null)
				try {
					dataFile.close();
				} catch (IOException ioe) {
					ioe.printStackTrace();
				}
		}
		
	}

}
