
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
from pytube import YouTube
import instaloader
import tweepy
import os
import requests
from moviepy.editor import VideoFileClip

class VideoDownloaderApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Social Media Video Downloader")
        self.master.geometry("600x400")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.output_dir = os.path.expanduser("~/Downloads")
        self.create_widgets()

    def create_widgets(self):
        # URL input
        self.url_label = ctk.CTkLabel(self.master, text="Video URL:")
        self.url_label.pack(pady=10)
        self.url_entry = ctk.CTkEntry(self.master, width=400)
        self.url_entry.pack()

        # Platform selection
        self.platform_label = ctk.CTkLabel(self.master, text="Platform:")
        self.platform_label.pack(pady=10)
        self.platform_var = tk.StringVar(value="YouTube")
        self.platform_combobox = ctk.CTkComboBox(self.master, variable=self.platform_var, 
                                                 values=["YouTube", "Instagram", "Twitter"])
        self.platform_combobox.pack()

        # Output format selection
        self.format_label = ctk.CTkLabel(self.master, text="Output Format:")
        self.format_label.pack(pady=10)
        self.format_var = tk.StringVar(value="mp4")
        self.format_combobox = ctk.CTkComboBox(self.master, variable=self.format_var, 
                                               values=["mp4", "mov", "avi"])
        self.format_combobox.pack()

        # Output directory selection
        self.dir_button = ctk.CTkButton(self.master, text="Select Output Directory", 
                                        command=self.select_directory)
        self.dir_button.pack(pady=20)

        # Download button
        self.download_button = ctk.CTkButton(self.master, text="Download", command=self.download_video)
        self.download_button.pack(pady=20)

    def select_directory(self):
        self.output_dir = filedialog.askdirectory() or self.output_dir

    def download_video(self):
        url = self.url_entry.get()
        platform = self.platform_var.get()
        output_format = self.format_var.get()

        if not url:
            messagebox.showerror("Error", "Please enter a valid URL")
            return

        try:
            if platform == "YouTube":
                self.download_youtube(url, output_format)
            elif platform == "Instagram":
                self.download_instagram(url, output_format)
            elif platform == "Twitter":
                self.download_twitter(url, output_format)
            
            messagebox.showinfo("Success", f"Video downloaded successfully to {self.output_dir}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def download_youtube(self, url, output_format):
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        temp_file = stream.download(output_path=self.output_dir)
        
        if output_format != 'mp4':
            final_file = os.path.splitext(temp_file)[0] + f".{output_format}"
            video = VideoFileClip(temp_file)
            video.write_videofile(final_file)
            os.remove(temp_file)
        else:
            final_file = temp_file

        return final_file

    def download_instagram(self, url, output_format):
        L = instaloader.Instaloader()
        post = instaloader.Post.from_shortcode(L.context, url.split("/")[-2])
        
        if post.is_video:
            video_url = post.video_url
            response = requests.get(video_url)
            
            temp_file = os.path.join(self.output_dir, f"instagram_video.mp4")
            with open(temp_file, 'wb') as f:
                f.write(response.content)
            
            if output_format != 'mp4':
                final_file = os.path.splitext(temp_file)[0] + f".{output_format}"
                video = VideoFileClip(temp_file)
                video.write_videofile(final_file)
                os.remove(temp_file)
            else:
                final_file = temp_file
            
            return final_file
        else:
            raise ValueError("The Instagram post does not contain a video")

    def download_twitter(self, url, output_format):
        # Note: Twitter API v2 requires authentication
        # This is a placeholder. You need to set up Twitter API credentials
        auth = tweepy.OAuthHandler("consumer_key", "consumer_secret")
        auth.set_access_token("access_token", "access_token_secret")
        api = tweepy.API(auth)

        tweet_id = url.split("/")[-1]
        tweet = api.get_status(tweet_id, tweet_mode="extended")
        
        if 'media' in tweet.entities:
            for media in tweet.extended_entities['media']:
                if media['type'] == 'video':
                    video_url = media['video_info']['variants'][0]['url']
                    response = requests.get(video_url)
                    
                    temp_file = os.path.join(self.output_dir, f"twitter_video.mp4")
                    with open(temp_file, 'wb') as f:
                        f.write(response.content)
                    
                    if output_format != 'mp4':
                        final_file = os.path.splitext(temp_file)[0] + f".{output_format}"
                        video = VideoFileClip(temp_file)
                        video.write_videofile(final_file)
                        os.remove(temp_file)
                    else:
                        final_file = temp_file
                    
                    return final_file
        
        raise ValueError("No video found in the tweet")

if __name__ == "__main__":
    root = ctk.CTk()
    app = VideoDownloaderApp(root)
    root.mainloop()

