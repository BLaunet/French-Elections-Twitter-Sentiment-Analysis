package nc;

import java.io.IOException;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.output.SequenceFileOutputFormat;
import org.apache.hadoop.util.GenericOptionsParser;

public class ReadNC {
	
	public static class NCMapper 
		extends Mapper<NullWritable, FloatArrayWritable, IntWritable, IntWritable> {
		
		public void map(NullWritable key, FloatArrayWritable value, Context context)
    		throws IOException, InterruptedException {
	
			// value = 3 x number of atoms
			context.write(new IntWritable(1), new IntWritable(value.get().length));
		}
	}
	
	public static class NCReducer 
		extends Reducer<IntWritable, IntWritable, IntWritable, Text> {
		
		/**
		 * Receives a sorted list of points assigned to the same cluster id and outputs each point in the cluster preceded by the cluster id.
		 */
		
		public void reduce(IntWritable key, Iterable<IntWritable> values, Context context)
    		throws IOException, InterruptedException {
				
			for (IntWritable v : values) {
				Text t =  new Text();
				int i = v.get();
				t.set(String.valueOf(i));
				context.write(key, t);
			}
		}
	}
		
	public static void main(String[] args) throws Exception {
		Configuration conf = new Configuration();
		String[] otherArgs = new GenericOptionsParser(conf, args).getRemainingArgs();
		if (otherArgs.length < 2) {
			System.err.println("Usage: ReadNC <in> <out> ");
			System.exit(2);
		}
		
		Job job = new Job(conf, "read netcdf format");
		
		job.setJarByClass(ReadNC.class);
		job.setMapperClass(NCMapper.class);
		
		job.setMapOutputKeyClass(IntWritable.class);
		job.setMapOutputValueClass(IntWritable.class);
		
	    job.setReducerClass(NCReducer.class);
		
		job.setInputFormatClass(WholeFileInputFormat.class);
	
		job.setOutputKeyClass(IntWritable.class);
		job.setOutputValueClass(Text.class);
		
		FileInputFormat.addInputPath(job, new Path(otherArgs[1]));
		FileOutputFormat.setOutputPath(job, new Path(otherArgs[2]));
	
		System.exit(job.waitForCompletion(true) ? 0 : 1);
	}
}
