def get_all_dashboards(site_display_name, server, auth):
    # Sign in to the Tableau server
    with server.auth.sign_in(auth):
        # Query to get the total number of workbooks
        query_total_workbooks = """
        query TotalWorkbooks($siteDisplayName: String!) {
            tableauSites(filter: { name: $siteDisplayName }) {
                workbooksConnection {
                    totalCount
                }
            }
        }
        """

        # Variables for the total workbooks query
        variables_total = {
            'siteDisplayName': site_display_name
        }

        # Execute the total workbooks query
        resp_total = server.metadata.query(query_total_workbooks, variables=variables_total)

        # Extract the total count of workbooks
        total_workbooks = resp_total['data']['tableauSites'][0]['workbooksConnection']['totalCount']
        print(f"Total Workbooks: {total_workbooks}")

        # Define pagination parameters
        batch_size = 10  # Number of workbooks per page
        num_batches = (total_workbooks + batch_size - 1) // batch_size  # Calculate total pages

        # Initialize a list to store all responses
        resp_all = []

        # The main query to retrieve dashboards with pagination
        query_dashboards = """
        query GetAllDashboards($siteDisplayName: String!, $first: Int!, $offset: Int!) {
            tableauSites(filter: { name: $siteDisplayName }) {
                name
                luid
                workbooksConnection(first: $first, offset: $offset) {
                    nodes {
                        name
                        luid
                        dashboards {
                            id
                            name
                            luid
                            path
                            workbook {
                                id
                                name
                                luid
                                projectName
                                tags {
                                    name
                                }
                                sheets {
                                    id
                                    name
                                    luid
                                    createdAt
                                    updatedAt
                                    sheetFieldInstances {
                                        name
                                        description
                                        isHidden
                                        id
                                    }
                                    worksheetFields {
                                        name
                                        description
                                        isHidden
                                        formula
                                        aggregation
                                        id
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        """

        # Loop through each page to retrieve all dashboards
        for i in range(num_batches):
            offset = i * batch_size
            variables_dashboards = {
                'siteDisplayName': site_display_name,
                'first': batch_size,
                'offset': offset
            }

            # Execute the dashboards query with pagination variables
            resp = server.metadata.query(query_dashboards, variables=variables_dashboards)

            # Append the response to the list
            resp_all.append(resp)

            # Optional: Print progress
            print(f"Retrieved batch {i + 1} of {num_batches}")

        # Return the list of all responses
        return resp_all
