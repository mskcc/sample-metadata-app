###############################################################HandsonTable Column configs #############################################################################

clinicalColHeaders = ['MRN', 'Investigator Sample ID', 'CMO Patient ID', 'CMO Sample ID', 'Sample Type', 'Species', 'Preservation', 'Tumor or Normal', 'Tissue Source', 'Sample Origin',
                      'Specimen Type', 'Gender', 'Parent Tumor Type', 'Tumor Type', 'Tissue Location', 'Ancestor Sample ID', 'Assay', 'Fastq Files']
clinicalColumns = [

    {
        'data': 'mrn',
        'readOnly': True
    },
    {
        'data': 'investigator_sampleid',
        'readOnly': True
    },
    {
        'data': 'cmo_patientid',
        'readOnly': True
    },
    {
        'data': 'cmo_sampleid',
        'readOnly': True
    },
    {
        'data': 'sample_type',
        'readOnly': True
    },
    {
        'data': 'species',
        'readOnly': True
    },
    {
        'data': 'preservation',
        'readOnly': True
    },
    {
        'data': 'tumor_normal',
        'readOnly': True
    },
    {
        'data': 'tissue_source',
        'readOnly': True
    },
    {
        'data': 'sample_origin',
        'readOnly': True
    },
    {
        'data': 'specimen_type',
        'readOnly': True
    },
    {
        'data': 'gender',
        'readOnly': True
    },
    {
        'data': 'parent_tumortype',
        'readOnly': True
    },
    {
        'data': 'tumortype',
        'readOnly': True
    },
    {
        'data': 'tissue_location',
        'readOnly': True
    },
    {
        'data': 'ancestor_sample',
        'readOnly': True
    },
    {
        'data': 'assay',
        'readOnly': True
    },
    {
        'data': 'fastq_data',
        'readOnly': True
    },

]

nonClinicalColHeaders = ['Investigator Sample ID', 'CMO Sample ID', 'Sample Type', 'Species', 'Preservation', 'Tumor or Normal', 'Tissue Source', 'Sample Origin',
                      'Specimen Type', 'Gender', 'Parent Tumor Type', 'Tumor Type', 'Tissue Location', 'Ancestor Sample ID', 'Assay', 'Fastq Files']

nonClinicalColumns = [
    {
        'data': 'investigator_sampleid',
        'readOnly': True
    },
    {
        'data': 'cmo_sampleid',
        'readOnly': True
    },
    {
        'data': 'sample_type',
        'readOnly': True
    },
    {
        'data': 'species',
        'readOnly': True
    },
    {
        'data': 'preservation',
        'readOnly': True
    },
    {
        'data': 'tumor_normal',
        'readOnly': True
    },
    {
        'data': 'tissue_source',
        'readOnly': True
    },
    {
        'data': 'sample_origin',
        'readOnly': True
    },
    {
        'data': 'specimen_type',
        'readOnly': True
    },
    {
        'data': 'gender',
        'readOnly': True
    },
    {
        'data': 'parent_tumortype',
        'readOnly': True
    },
    {
        'data': 'tumortype',
        'readOnly': True
    },
    {
        'data': 'tissue_location',
        'readOnly': True
    },
    {
        'data': 'ancestor_sample',
        'readOnly': True
    },
    {
        'data': 'assay',
        'readOnly': True
    },
    {
        'data': 'fastq_data',
        'readOnly': True
    },

]

adminColHeaders = ['MRN', 'Investigator Sample ID', 'CMO Patient ID', 'CMO Sample ID', 'Sample Type', 'Species', 'Preservation', 'Tumor or Normal', 'Tissue Source', 'Sample Origin',
                      'Specimen Type', 'Gender', 'Parent Tumor Type', 'Tumor Type', 'Tissue Location', 'Ancestor Sample ID', 'Assay', 'Fastq Files']
adminColumns = [
    {
        'data': 'mrn',
        'readOnly': True
    },
    {
        'data': 'investigator_sampleid',
        'readOnly': True
    },
    {
        'data': 'cmo_patientid',
        'readOnly': True
    },
    {
        'data': 'cmo_sampleid',
        'readOnly': True
    },
    {
        'data': 'sample_type',
        'readOnly': True
    },
    {
        'data': 'species',
        'readOnly': True
    },
    {
        'data': 'preservation',
        'readOnly': True
    },
    {
        'data': 'tumor_normal',
        'readOnly': True
    },
    {
        'data': 'tissue_source',
        'readOnly': True
    },
    {
        'data': 'sample_origin',
        'readOnly': True
    },
    {
        'data': 'specimen_type',
        'readOnly': True
    },
    {
        'data': 'gender',
        'readOnly': True
    },
    {
        'data': 'parent_tumortype',
        'readOnly': True
    },
    {
        'data': 'tumortype',
        'readOnly': True
    },
    {
        'data': 'tissue_location',
        'readOnly': True
    },
    {
        'data': 'ancestor_sample',
        'readOnly': True
    },
    {
        'data': 'assay',
        'readOnly': True
    },
    {
        'data': 'fastq_data',
        'readOnly': True
    },
]

settings = {
    'columnSorting': True,
    'filters': True,
    'autoColumnSize': True,
    'width': '100%',
    'height': 500,
    'colWidths': [200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200,
                  200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200,
                  200, 200, 200, 200, 200, 200, 200],
    'manualColumnResize': True,
    'rowHeaders': True,
    'colHeaders': True,
    'search': True,
    'dropdownMenu': ['filter_by_condition', 'filter_action_bar'],
}

########################################################################################################################################