import streamlit as st
import pandas as pd
import plotly.express as px

# Create Interface
st.set_page_config(layout="wide")
genre = st.sidebar.radio(
    "Select The Questions",
    ["Question 1: Top 5 Popular Presentations", "Question 2: What is your weighted score?", "Question 3: %Pass of the Assignments"],
    captions = ["View the top 5 popular presentations.", "View your weighted score.", "View the %pass of the assessment."])

if genre == 'Question 1: Top 5 Popular Presentations':
    # Load the Data
    studentinfo = pd.read_csv("studentInfo.csv")

    # Drop the unnecessary columns
    studentinfo_cleaned = studentinfo.drop(
        ['imd_band', 'disability', 'code_module', 'code_presentation', 'num_of_prev_attempts', 'studied_credits'],
        axis=1)

    # Filter the students who didn't pass the courses "Fail", "Withdrawn"
    filtered_studentinfo = studentinfo_cleaned[studentinfo['final_result'].isin(['Pass', 'Distinction'])]
    filtered_studentinfo['module_presentation'] = studentinfo['code_module'] + "_" + studentinfo['code_presentation']

    # Convert "code_presentation" into "time"
    filtered_studentinfo['time'] = studentinfo['code_presentation'].str.replace('[^0-9]', '', regex=True).astype(int)
    #st.write(filtered_studentinfo)

    # Initialize the Streamlit app
    st.title("Top 5 Popularity of Module Presentations")

    # Sidebar filters
    gender_filter = st.sidebar.multiselect("Select Gender", options=filtered_studentinfo['gender'].unique())
    region_filter = st.sidebar.multiselect("Select Region", options=filtered_studentinfo['region'].unique())
    education_filter = st.sidebar.multiselect("Select Highest Education",
                                              options=filtered_studentinfo['highest_education'].unique())
    age_band_filter = st.sidebar.multiselect("Select Age Band", options=filtered_studentinfo['age_band'].unique())

    # Adding a clickable year filter
    year_option = st.sidebar.radio("Select Year", options=["2013", "2014", "2013&2014"])

    # Apply all filters
    filtered_data = filtered_studentinfo
    if year_option == "2013":
        filtered_data = filtered_data[filtered_data['time'] == 2013]
    elif year_option == "2014":
        filtered_data = filtered_data[filtered_data['time'] == 2014]
    elif year_option == "2013&2014":
        filtered_data = filtered_data[filtered_data['time'].isin([2013, 2014])]

    if gender_filter:
        filtered_data = filtered_data[filtered_data['gender'].isin(gender_filter)]
    if region_filter:
        filtered_data = filtered_data[filtered_data['region'].isin(region_filter)]
    if education_filter:
        filtered_data = filtered_data[filtered_data['highest_education'].isin(education_filter)]
    if age_band_filter:
        filtered_data = filtered_data[filtered_data['age_band'].isin(age_band_filter)]

    # Group by 'module_presentation' and count the number of students
    module_popularity_filtered = filtered_data.groupby('module_presentation')['id_student'].nunique()
    #st.write(module_popularity_filtered)


    # Sort and get the top 10
    top_5_modules_filtered = module_popularity_filtered.sort_values(ascending=False).head(5)

    # Create a horizontal bar chart with text annotations
    fig_filtered = px.bar(top_5_modules_filtered, y=top_5_modules_filtered.index, x=top_5_modules_filtered.values,
                          labels={'y': 'Module Presentation', 'x': 'Number of Students'},
                          title='Top 5 Popular Module Presentations',
                          orientation='h')  # 'h' for horizontal bars

    # Add text on each bar to show the exact value
    fig_filtered.update_traces(text=top_5_modules_filtered.values, textposition='outside')
    # Reverse the order of the y-axis to have the highest value at the top
    fig_filtered.update_yaxes(autorange="reversed")

    # Display the plot
    st.plotly_chart(fig_filtered)


elif genre == 'Question 2: What is your weighted score?':
    # Title and Instructions
    st.title("What is your weighted score?")
    st.caption("Choose your student id to see your weighted score and detailed scores")

    # Load the Data
    at = pd.read_csv("assessments.csv")
    stat = pd.read_csv("studentAssessment.csv")

    # Combine 'code_module' and 'code_presentation' into one column
    at['module_presentation'] = at['code_module'] + "_" + at['code_presentation']

    # Merge the Data Frames on 'id_assessment'
    combined_data = pd.merge(stat, at, on='id_assessment', how='left')

    # Selecting Required Columns
    selected_columns = ['id_student', 'id_assessment', 'score', 'assessment_type', 'module_presentation', 'weight']
    combined_data = combined_data[selected_columns]

    # Calculate the Total Weight for Each Student per Course
    combined_data['total_weight_per_student'] = combined_data.groupby(['id_student', 'module_presentation'])[
        'weight'].transform('sum')

    # Normalize the Weights for Each Student
    combined_data['normalized_weight'] = combined_data['weight'] / combined_data['total_weight_per_student']

    # Calculate Weighted Scores
    combined_data['weighted_score'] = combined_data['score'] * combined_data['normalized_weight']

    # Dropdown for Student ID in Sidebar
    unique_student_ids = combined_data['id_student'].unique()
    student_id = st.sidebar.selectbox('Choose a student ID', unique_student_ids)

    # Filter Data for the Selected Student ID
    filtered_data = combined_data[combined_data['id_student'] == student_id]

    # Create a Combined Label for Score and Weight
    filtered_data['score_weight'] = filtered_data['score'].astype(str) + ' (Weight: ' + filtered_data['weight'].astype(
        str) + ')'
    # Display Sum of Weighted Scores for the Selected Student
    total_weighted_score = filtered_data.groupby('module_presentation')['weighted_score'].sum()
    st.write("Total Weighted Scores by Course for Student ID:", student_id)
    st.table(total_weighted_score)

    # Bar Chart for Detailed Scores and Assessment Types
    chart_data = filtered_data[['id_assessment', 'score', 'assessment_type', 'score_weight']]
    fig = px.bar(chart_data, x='id_assessment', y='score', color='assessment_type', text='score_weight',
                 title=f"Detailed Scores and Assessment Types for Student ID: {student_id}")
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    st.plotly_chart(fig)


else:
    # Title and Instructions
    st.title("% Pass of the Assessments of Different Presentations")
    st.caption("Select the module, presentation, and specific assessment")

    # Read the data
    at = pd.read_csv("assessments.csv")
    stat = pd.read_csv("studentAssessment.csv")

    # Merge the dataframes on 'id_assessment'
    merged_df = pd.merge(stat, at, on='id_assessment')

    # Sidebar for filters
    st.sidebar.title("Filters")
    selected_module = st.sidebar.selectbox("Select a Module", options=merged_df['code_module'].unique())
    selected_presentation = st.sidebar.selectbox("Select a Presentation",
                                                 options=merged_df['code_presentation'].unique())

    # Multi-select dropdown for selecting 'id_assessment'
    assessment_options = merged_df[(merged_df['code_module'] == selected_module) &
                                   (merged_df['code_presentation'] == selected_presentation)]['id_assessment'].unique()
    selected_assessments = st.sidebar.multiselect("Select Assessments", options=assessment_options)

    # Create a layout with two columns
    col1, col2 = st.columns(2)
    current_col = col1

    # Iterate over each selected assessment and display a pie chart
    for i, selected_assessment in enumerate(selected_assessments):
        # Alternate between the two columns
        if i % 2 == 0:
            current_col = col1
        else:
            current_col = col2

        # Filter the data for the selected assessment
        filtered_df = merged_df[merged_df['id_assessment'] == selected_assessment]

        # Filter scores above and below 60
        above_60 = filtered_df[filtered_df['score'] >= 60].shape[0]
        below_60 = filtered_df[filtered_df['score'] < 60].shape[0]
        total = above_60 + below_60

        # Prepare data for the pie chart with custom labels for count and percentage
        scores_data = {
            'Score Range': ['Above or Equal to 60', 'Below 60'],
            'Count': [above_60, below_60],
            'Percentage': [f'{above_60 / total:.2%}', f'{below_60 / total:.2%}'] if total > 0 else ['0%', '0%']
        }

        df_scores = pd.DataFrame(scores_data)

        # Create a pie chart with custom textinfo
        fig = px.pie(df_scores, names='Score Range', values='Count',
                     title=f'Distribution of Scores for Assessment {selected_assessment}')
        fig.update_traces(textinfo='label+percent', hoverinfo='label+value', text=df_scores['Percentage'])

        # Display the pie chart in the appropriate column
        with current_col:
            st.plotly_chart(fig, use_container_width=True)