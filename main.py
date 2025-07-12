import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scrape_jobs import JobScraper
import time
from datetime import datetime
import re
from doc_loader import load_docs

# Page configuration
st.set_page_config(
    page_title="Job Scraper Dashboard",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .job-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .source-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.75rem;
        font-weight: bold;
        color: white;
    }
    .linkedin-badge {
        background-color: #0077b5;
    }
    .naukri-badge {
        background-color: #4a90e2;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">💼 AI Job Scraper Dashboard </h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar for search parameters
    with st.sidebar:
        st.header("🔍 Search Parameters")
        
        job_title = st.text_input(
            "Job Title",
            value="Python Developer",
            help="Enter the job title you want to search for"
        )
        
        location = st.text_input(
            "Location (Optional)",
            value="",
            help="Enter location (e.g., Mumbai, Delhi, Bangalore)"
        )
        
        max_pages = st.slider(
            "Maximum Pages to Scrape",
            min_value=1,
            max_value=5,
            value=2,
            help="Number of pages to scrape from each site"
        )
        
        headless_mode = st.checkbox(
            "Headless Mode",
            value=True,
            help="Run browser in background (faster but no visual feedback)"
        )

        uploaded_file = st.file_uploader(
            "Upload resume for AI matching", 
            type="pdf",
            help="Upload resume for AI matching in pdf format")
        
        scrape_button = st.button(
            "🚀 Start Scraping",
            type="primary",
            use_container_width=True
        )
    
    # Main content area
    if scrape_button:
        if not job_title.strip():
            st.error("Please enter a job title to search for.")
            return
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Initialize scraper
            status_text.text("Initializing web scraper...")
            progress_bar.progress(10)
            
            with JobScraper(headless=headless_mode) as scraper:
                status_text.text("Scraping jobs from LinkedIn and Naukri...")
                progress_bar.progress(30)
                
                # Scrape jobs
                df = scraper.scrape_all_jobs(job_title, location, max_pages)
                progress_bar.progress(50)

                try:
                    ai_job_list=load_docs(uploaded_file,df)
                    progress_bar.progress(80)
                except Exception as e:
                    status_text.text(f"Not able to generate AI Jobs: {e}")
                    st.warning(f"Not able to generate the AI matched Jobs: {e}")
                    ai_job_list=[]

                
                status_text.text("Processing results...")
                progress_bar.progress(100)
                
                # Store results in session state
                
                st.session_state.job_data = df
                st.session_state.ai_job_list=ai_job_list
                st.session_state.search_params = {
                    'job_title': job_title,
                    'location': location,
                    'max_pages': max_pages,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    
                }
                
                status_text.text("✅ Scraping completed successfully!")
                time.sleep(1)
                status_text.empty()
                progress_bar.empty()
                
        except Exception as e:
            st.error(f"An error occurred during scraping: {str(e)}")
            st.info("Please check your internet connection and try again.")
            return
    
    # Display results if available
    if 'job_data' in st.session_state and not st.session_state.job_data.empty:
        display_results(st.session_state.job_data, st.session_state.ai_job_list, st.session_state.search_params)
    elif 'job_data' in st.session_state:
        st.warning("No jobs found for the given search criteria. Try different keywords or location.")
    else:
        # Welcome message
        st.info("👆 Use the sidebar to configure your job search and click 'Start Scraping' to begin!")
        
        # Sample data preview
        sample_data = create_sample_data()
        display_results(sample_data, [],{
            'job_title': 'Sample Jobs',
            'location': 'Various',
            'max_pages': 2,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }, is_sample=True)

def display_results(df, ai_job_list,search_params, is_sample=False):
    """Display the scraped job results"""
    
    # Search summary
    col1, col2, col3 = st.columns(3)
    
    st.markdown("---")
    
    # Analytics section
    if len(df) > 0:
        st.subheader("📊 Job Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Jobs by source
            source_counts = df['source'].value_counts()
            fig_source = px.pie(
                values=source_counts.values,
                names=source_counts.index,
                title="Jobs by Source",
                color_discrete_map={'LinkedIn': '#0077b5', 'Naukri': '#4a90e2'}
            )
            fig_source.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_source, use_container_width=True)
        
        with col2:
            # Top companies
            if 'company' in df.columns:
                company_counts = df['company'].value_counts().head(10)
                fig_companies = px.bar(
                    x=company_counts.values,
                    y=company_counts.index,
                    orientation='h',
                    title="Top 10 Companies",
                    labels={'x': 'Number of Jobs', 'y': 'Company'}
                )
                fig_companies.update_layout(yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig_companies, use_container_width=True)
    
    # Filters
    st.subheader("🔍 Filter Results")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        source_filter = st.multiselect(
            "Filter by Source",
            options=df['source'].unique(),
            default=df['source'].unique()
        )
    
    with col2:
        if 'company' in df.columns:
            companies = df['company'].unique()
            company_filter = st.multiselect(
                "Filter by Company",
                options=companies,
                default=companies[:10] if len(companies) > 10 else companies
            )
        else:
            company_filter = []
    
    with col3:
        if 'location' in df.columns:
            locations = df['location'].unique()
            location_filter = st.multiselect(
                "Filter by Location",
                options=locations,
                default=locations[:10] if len(locations) > 10 else locations
            )
        else:
            location_filter = []
    
    # Apply filters
    filtered_df = df[df['source'].isin(source_filter)]
    if company_filter and 'company' in df.columns:
        filtered_df = filtered_df[filtered_df['company'].isin(company_filter)]
    if location_filter and 'location' in df.columns:
        filtered_df = filtered_df[filtered_df['location'].isin(location_filter)]
    
    # Job listings
    if len(ai_job_list)!=0:
        st.subheader(f"💼 AI Matched Job Listings ({len(ai_job_list)} jobs)")
        
        if len(ai_job_list) > 0:
            # Pagination
            jobs_per_page = 4
            total_pages = (len(ai_job_list) - 1) // jobs_per_page + 1
            
            if total_pages > 1:
                page = st.selectbox("Page", range(1, total_pages + 1))
                start_idx = (page - 1) * jobs_per_page
                end_idx = start_idx + jobs_per_page
                page_df = ai_job_list.iloc[start_idx:end_idx]
            else:
                page_df = ai_job_list
            
            # Display jobs
            for idx, job in page_df.iterrows():
                display_job_card(job)
        st.markdown("---")
        col1, col2 = st.columns([1, 4])
        with col1:
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"jobs_{search_params['job_title'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        st.markdown("---")
        col1, col2 = st.columns([1, 4])
        with col1:
            csv = ai_job_list.to_csv(index=False)
            st.download_button(
                label="📥 Download AI matched JOB CSV",
                data=csv,
                file_name=f"jobs_{search_params['job_title'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    elif len(filtered_df) !=0:
        st.subheader(f"💼 Job Listings ({len(filtered_df)} jobs)")
        
        if len(filtered_df) > 0:
            # Pagination
            jobs_per_page = 4
            total_pages = (len(filtered_df) - 1) // jobs_per_page + 1
            
            if total_pages > 1:
                page = st.selectbox("Page", range(1, total_pages + 1))
                start_idx = (page - 1) * jobs_per_page
                end_idx = start_idx + jobs_per_page
                page_df = filtered_df.iloc[start_idx:end_idx]
            else:
                page_df = filtered_df
            
            # Display jobs
            for idx, job in page_df.iterrows():
                display_job_card(job)
            
            # Download option
        st.markdown("---")
        col1, col2 = st.columns([1, 4])
        with col1:
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"jobs_{search_params['job_title'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
    else:
        st.info("No jobs match the selected filters.")

def display_job_card(job):
    """Display individual job card"""
    
    job_link = job.get('job_link', '#')
    link_text = "🔗 View Job" if job_link != "N/A" and job_link != "#" else "Link not available"
    print(job['title'])
    # Build job card HTML


    card_html = f"""
    <div class="job-card" style="margin-bottom: 2rem;">
        <h3 style="margin: 0; color: #1f77b4;">{job['title']}</h3>
        <p style="margin: 0.5rem 0; font-size: 1.1rem; font-weight: 500;">🏢 {job['company']}</p>
        <p style="margin: 0.5rem 0; color: #666;">📍 {job['location']}</p>
    """
    
    # Add additional fields based on source
    if 'Experience' in job and job['experience'] != 'N/A':
        card_html += f'<p style="margin: 0.5rem 0; color: #666;">💼 Experience: {job["experience"]}</p>'
    
    if 'salary' in job and job['salary'] != 'N/A':
        card_html += f'<p style="margin: 0.5rem 0; color: #666;">💰 Salary: {job["salary"]}</p>'
    
    if 'posted_date' in job and job['posted_date'] != 'N/A':
        card_html += f'<p style="margin: 0.5rem 0; color: #666;">📅 Posted: {job["posted_date"]}</p>'
    
    card_html += "</div>"
    
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Add link button if available
    if job_link != "N/A" and job_link != "#":
        st.markdown(f'<a href="{job_link}" target="_blank" style="text-decoration: none;">{link_text}</a>', unsafe_allow_html=True)
    
    st.markdown("---")

def create_sample_data():
    """Create sample data for demonstration"""
    sample_jobs = [
        {
            'title': 'Senior Python Developer',
            'company': 'Tech Solutions Inc.',
            'location': 'Mumbai, Maharashtra',
            'experience': '3-5 years',
            'salary': '₹8-12 LPA',
            'posted_date': '2 days ago',
            'job_link': '#',
            'source': 'LinkedIn'
        },
        {
            'title': 'Python Backend Engineer',
            'company': 'StartupXYZ',
            'location': 'Bangalore, Karnataka',
            'experience': '2-4 years',
            'salary': '₹6-10 LPA',
            'posted_date': '1 day ago',
            'job_link': '#',
            'source': 'Naukri'
        },
        {
            'title': 'Full Stack Python Developer',
            'company': 'Digital Innovations',
            'location': 'Delhi, NCR',
            'experience': '4-6 years',
            'salary': '₹10-15 LPA',
            'posted_date': '3 days ago',
            'job_link': '#',
            'source': 'LinkedIn'
        },
        {
            'title': 'Python Data Engineer',
            'company': 'DataCorp',
            'location': 'Pune, Maharashtra',
            'experience': '3-5 years',
            'salary': '₹9-13 LPA',
            'posted_date': '1 week ago',
            'job_link': '#',
            'source': 'Naukri'
        }
    ]
    
    return pd.DataFrame(sample_jobs)

if __name__ == "__main__":
    main()